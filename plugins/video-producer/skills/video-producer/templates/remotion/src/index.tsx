import React from "react";
import {AbsoluteFill, Composition, interpolate, registerRoot, useCurrentFrame} from "remotion";

const Title = ({title}: {title: string}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 12], [0, 1], {extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{
      alignItems: "center", justifyContent: "center", background: "#111827",
      color: "#F9FAFB", fontSize: 74, fontFamily: "sans-serif", textAlign: "center", padding: 100,
    }}>
      <div style={{opacity}}>{title}</div>
    </AbsoluteFill>
  );
};

const Root = () => (
  <Composition id="Title" component={Title} defaultProps={{title: "Video Producer"}}
    width={1080} height={1920} fps={30} durationInFrames={90} />
);

registerRoot(Root);
