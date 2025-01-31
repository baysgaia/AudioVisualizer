FROM node:18-alpine
WORKDIR /app/node

# 必要ライブラリのインストール
RUN apk add --no-cache python3 make g++ cairo-dev pango-dev jpeg-dev giflib-dev

COPY package.json package-lock.json ./

RUN npm install

COPY . .
CMD ["node", "src/index.js"] 