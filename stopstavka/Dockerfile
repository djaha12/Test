FROM node:22-alpine

WORKDIR /app
ENV NODE_ENV=production \
    PORT=8080 \
    DATA_DIR=/data

COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY public ./public
COPY server ./server

RUN mkdir -p /data && chown node:node /data
VOLUME /data
EXPOSE 8080
USER node

CMD ["node", "--disable-warning=ExperimentalWarning", "server/index.js"]
