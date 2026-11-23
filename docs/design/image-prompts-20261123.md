# UI/UXリニューアルの画像記録

生成方法：組み込み `image_gen`（CLI/APIキーを使う経路は未使用）。生成物を目視確認し、内容を変更せずWebPで配信用に書き出した。PNG原本は生成ツールの保存先に保持。人物・ロゴ・実在農園の写真を使用していない。ページ上ではAI生成のイメージとして表示し、実在の生産者カードや販売商品の写真として紐付けない。

## 保存した配信用画像

- `shop/images/harvest-hero.webp` — 1536×1024、276,908 bytes
- `shop/images/fruit-editorial.webp` — 960×640、104,826 bytes
- `shop/images/rice-editorial.webp` — 960×640、90,000 bytes
- `shop/images/pantry-editorial.webp` — 960×640、127,686 bytes

## 最終プロンプト

### ヒーロー・野菜

Use case: photorealistic-natural. Asset type: original wide hero photograph for a Japanese agricultural producer discovery website, NOT an actual producer profile. Create a premium natural editorial still-life photograph, landscape 3:2, of a shallow dark wooden harvest crate overflowing with fresh seasonal leafy greens, carrots with soil, small radishes and a few tomatoes, resting beside cultivated crop rows on a quiet Japanese countryside farm. Warm low autumn sunlight, tactile green leaves and earth, sophisticated food magazine art direction, real imperfect produce, subtle cinematic depth, deep olive greens and terracotta accents, documentary realism. Frame the crate in the right two thirds and leave the upper left calm soft farmland background for optional website typography; no people or identifiable faces, no structures or famous locations, no logos, no writing or labels, no watermark, no UI or collage. This will be labelled as an AI-generated concept image on the website and must not imply a specific real farm or merchandise.

### 果物

Premium editorial food photograph for a category tile in a Japanese farm discovery website. Landscape 3:2. An intimate still life of three imperfect red apples, one cut persimmon and a few small mandarins with leaves on a dark worn wooden farm table, autumn natural window light, deep warm shadows, tactile skin, restrained food-magazine styling, photorealistic, close composition, no branding, no text, no packaging labels, no watermark, no people. Generic AI concept, not merchandise from a real farm.

### 米

Premium editorial food photograph for a category tile in a Japanese farm discovery website. Landscape 3:2. Newly harvested short-grain Japanese rice in a shallow natural wooden masu box, a small off-white ceramic bowl of fresh steamed rice, several golden rice stalks resting on a textured warm charcoal table. Soft sidelight, detailed individual rice grains, authentic restrained Japanese food magazine art direction, photorealistic. No people, no logo, no writing, no watermark, not tied to a real producer or brand.

### 加工品

Premium editorial food photograph for an agricultural category tile in a Japanese farm discovery website. Landscape 3:2. Two simple unlabelled glass jars of deep amber fruit preserve and scarlet tomato sauce, a rustic slice of bread and a small wooden spoon, on linen and a weathered wood table. Gentle morning light, rich natural colors, sophisticated tactile food magazine still life, photorealistic, no people, no logo, no text or labels, no watermark. Generic AI concept, not any real product.
