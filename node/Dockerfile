FROM node:18-alpine
WORKDIR /app

# canvas のビルドに必要な依存をインストール
# python3, make, g++, cairo-dev など
RUN apk add --no-cache \
  python3 \
  make \
  g++ \
  cairo-dev \
  pango-dev \
  jpeg-dev \
  giflib-dev

# ルートの package*.json をコピー
COPY ../package*.json ./
RUN npm install

COPY ../ ./
CMD ["npm", "start"]