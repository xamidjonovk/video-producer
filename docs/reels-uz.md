# Birinchi montajdayoq gapga mos Reel olish

Video Producer’ga tasdiqlangan ovoz, mavjud kadrlar va tomoshabin nimani tushunib olishi kerakligini bering. Quyidagi misolda vazifa oddiy savolni tushuntirishdan iborat. Qaydni qidirib topish bilan yangi dalil asosida xulosani yangilash ekranda qanday farq qiladi?

## Nusxalab ishlatish uchun topshiriq

> Shu ovoz va kadrlarimdan vertikal Reel tayyorla. Matn va ovoz tasdiqlangan. Obsidian haqida gapirsam, qidiruvdan qayd ochilishini ko‘rsat. Yangi dalil xulosani qanday o‘zgartirishini qora fonda animatsiya qil. Yuzimni kirishda ishlat, keyin gapga mos haqiqiy kadrlar qo‘sh. Telefonda har bir so‘z aniq eshitilsin. MP4, subtitr va tahrirlanadigan loyihani ber.

Agar yangi lab sinxroni kerak bo‘lsa, qaysi video tabiiyroq chiqqanini va qaysi ovoz tasdiqlanganini ayting. Shu ijrodan yangi dubl tayyorlash vazifasi berilganda plugin avval yuz ko‘rinadigan oraliqlarni tanlaydi. Pullik generatsiya uchun narx va ruxsat doirasi alohida tekshiriladi.

## Bitta g‘oyaning beshta kadri

Quyidagi vaqtlar o‘ylab topilgan 15 soniyalik misolga tegishli. Montajchi ularni sizning ovozingizdagi haqiqiy so‘z va pauzalarga moslaydi. Narx haqidagi qaydlar misol uchun yozilgan.

| Vaqt | Ovozdagi fikr | Tomoshabin nimani ko‘radi? |
| --- | --- | --- |
| 0–2 s | “Eski qaroringizni topdingiz.” | Kadrda boshlovchi. “Topdingiz” so‘zida ekran yozuviga kesiladi. |
| 2–5 s | “Martda arzon tarifni tanlagansiz.” | Obsidian qidiruviga “tarif” yoziladi. “Mart qarori” qaydi ochiladi. Tanlangan jumla telefonda o‘qiladigan kattalikda qoladi. |
| 5–8 s | “Iyunda mijoz tezlikni so‘radi.” | Yuqoridan olingan yaqin planda qo‘l iyundagi so‘rovda “24 soatda” degan joyni belgilaydi. O‘zingiz suratga olgan hujjat yoki ruxsatli namuna ishlatiladi. |
| 8–12 s | “Endi mezon o‘zgardi.” | Belgilangan satr qora fondagi diagrammaga o‘tadi. “Iyun • 24 soat” dalilidan qarorga chiziq tortiladi. “Eng arzon” o‘rniga “Bir kunda yetkazish” paydo bo‘ladi. |
| 12–15 s | “Qaysi dalil qarorni o‘zgartirganini ham ko‘rasiz.” | Kadr ikkiga bo‘linadi. Chapda martdagi qayd, o‘ngda iyundagi dalil va yangi xulosa birga qoladi. Ovoz tugaguncha ikkalasini o‘qishga vaqt bor. |

“To‘rtta qatlam” degan jumlada miya to‘liq ko‘rinishi mumkin. Har bir nom aytilganda aynan o‘sha qatlam yorishsin. “Tabiiyroq” degan tuzatishda esa boshlovchining yuzi yaqin planda ko‘riladi, dublning boshlanishi, o‘rtasi va oxiri ovoz bilan solishtiriladi. Kuchliroq ritmga o‘tish uchun boshlovchi kadrini tezlatish shart emas.

## Tahrir so‘rash

Vaqt va ko‘rinadigan natijani ayting. Masalan, “0:04 da qidiruv natijasi juda mayda. Qayd ochilishiga yaqinlash va nomini o‘qishga vaqt ber” yoki “0:09 da effekt oxirgi so‘zni bosib ketgan. O‘sha effektni pasaytir.” Plugin mavjud loyiha, ovoz va tasdiqlangan kadrlarni qayta ishlata oladi.

## Terminal orqali ko‘rish

Repo ildizidan montaj rejasi va mavjud vositalarni ko‘rish uchun quyidagi buyruqlarni ishlating. Birinchi buyruq bosqichlarni chiqaradi. Videoni yaratish uchun yuqoridagi topshiriqni plagin o‘rnatilgan, fayllar va terminalga kira oladigan assistentga bering.

```sh
python plugins/video-producer/skills/video-producer/vp.py plan . motion-reel
python plugins/video-producer/skills/video-producer/vp.py plan . motion-reel presenter-clone
python plugins/video-producer/skills/video-producer/vp.py doctor .
```

[O‘rnatish va texnologiyalar](../README.md) · [Plaginning montaj qo‘llanmasi](../plugins/video-producer/skills/video-producer/references/motion-reel.md)
