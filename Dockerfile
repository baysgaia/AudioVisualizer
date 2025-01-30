FROM node:18-alpine
WORKDIR /app

# 必要ライブラリのインストール
RUN apk add --no-cache python3 make g++ cairo-dev pango-dev jpeg-dev giflib-dev

COPY package*.json ./
RUN npm install

COPY . .
CMD ["npm", "start"] 