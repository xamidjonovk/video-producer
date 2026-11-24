"""Color controls and delivery measurements for the local FFmpeg workflow."""

import json
import math
import re


REC709_TAGS = ('-color_primaries', 'bt709', '-color_trc', 'bt709',
               '-colorspace', 'bt709', '-color_range', 'tv')
TRACK_GAINS = {'dialogue': 1.0, 'music': 0.16, 'ambience': 0.12, 'foley': 0.36}


def color_source(video):
    details = json.dumps(video).lower()
    if 'dovi configuration' in details or 'dolby vision' in details or 'dvhe' in details or 'dvh1' in details:
        return 'dolby-vision'
    if 'smpte2084' in details:
        return 'pq'
    if 'arib-std-b67' in details:
        return 'hlg'
    return 'sdr'


def color_filters(video, grade, number, tone_map):
    source = color_source(video)
    details = json.dumps(video).lower()
    if source == 'dolby-vision':
        raise ValueError('Dolby Vision needs a color-managed SDR export from Resolve or another compatible editor.')
    if source in ('pq', 'hlg'):
        if not tone_map:
            raise ValueError('Enable color.hdr_to_sdr for tagged PQ/HLG or supply a color-managed SDR export.')
        transfer = 'smpte2084' if source == 'pq' else 'arib-std-b67'
        source_range = 'full' if ('(pc,' in details or isinstance(video, dict) and
                                  video.get('color_range') == 'pc') else 'limited'
        filters = [f'zscale=pin=bt2020:tin={transfer}:min=bt2020nc:rin={source_range}:p=bt709:t=linear:npl=100',
                   'format=gbrpf32le', 'tonemap=tonemap=mobius:desat=2',
                   'zscale=pin=bt709:tin=linear:t=bt709:m=bt709:r=limited', 'format=yuv420p']
    elif isinstance(video, dict) and video.get('color_transfer') in ('log', 'log_sqrt', 'smpte428'):
        raise ValueError('Supply a color-managed SDR export for log or cinema transfer material.')
    elif 'bt2020' in details and '/unknown' in details:
        raise ValueError('The BT.2020 file has incomplete color tags. Confirm its input color space in Resolve and export SDR.')
    elif any(tag in details for tag in ('bt2020', 'smpte432', 'smpte431', 'iec61966-2-1')):
        filters = ['zscale=p=bt709:t=bt709:m=bt709:r=limited']
    else:
        matrix = 'in_color_matrix=auto:out_color_matrix=bt709:out_range=tv'
        filters = [f'scale={matrix}']
    controls = {'brightness': (-0.25, 0.25), 'contrast': (0.5, 1.5),
                'saturation': (0, 2), 'gamma': (0.5, 2)}
    unknown = grade.keys() - controls.keys()
    if unknown:
        raise ValueError(f'Unknown grade controls: {", ".join(sorted(unknown))}')
    if grade:
        options = ':'.join(f'{name}={number(value, f"grade.{name}", *controls[name]):g}'
                           for name, value in grade.items())
        filters.append(f'eq={options}')
    return filters


def loudness_filter(target, peak, measured=None):
    base = f'loudnorm=I={target:g}:TP={peak:g}:LRA=11'
    if measured and measured['input_i'] is not None:
        options = {'measured_I': measured['input_i'], 'measured_TP': measured['input_tp'],
                   'measured_LRA': measured['input_lra'], 'measured_thresh': measured['input_thresh'],
                   'offset': measured['target_offset']}
        if all(value is not None for value in options.values()):
            base += ':linear=true:' + ':'.join(f'{name}={value:g}' for name, value in options.items())
    return base + ':print_format=json'


def measure_loudness(run, executable, path, target, peak):
    result = run(executable, '-nostdin', '-hide_banner', '-i', path, '-vn',
                 '-af', loudness_filter(target, peak), '-f', 'null', '-')
    match = re.search(r'\{\s*"input_i"\s*:.*?\}', result.stderr, re.DOTALL)
    if not match:
        raise ValueError('FFmpeg did not report loudness for the audio stream.')
    data = json.loads(match.group())
    values = {key: float(data[key]) for key in
              ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')}
    return {key: value if math.isfinite(value) else None for key, value in values.items()}


def measure_picture(run, executable, path):
    measurement = run(executable, '-nostdin', '-hide_banner', '-i', path, '-an',
                      '-vf', 'fps=1:start_time=0:round=up,signalstats,metadata=mode=print:file=-',
                      '-f', 'null', '-')
    values = re.findall(r'lavfi\.signalstats\.YAVG=([\d.]+)', measurement.stdout)
    if not values:
        return {'samples': 0}
    levels = [float(value) for value in values]
    return {'samples': len(levels), 'average_luma_min': min(levels), 'average_luma_max': max(levels)}
