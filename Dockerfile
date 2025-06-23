FROM node:16

WORKDIR /app
COPY package*.json ./
RUN npm install

# If using Tesseract.js, install system dependency:
RUN apt-get update && apt-get install -y tesseract-ocr

COPY . .

CMD ["node", "src/index.js"]
