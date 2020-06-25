FROM node:10

# Create app directory
WORKDIR /usr/src/app

# Create Arguments
ARG PORT_ARG=3000
ENV PORT=$PORT_ARG

ARG REACT_APP_COMMENTS_ON
ENV REACT_APP_COMMENTS_ON=$REACT_APP_COMMENTS_ON

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json ./

RUN npm install
# If you are building your code for production
# RUN npm ci --only=production

# Bundle app source
COPY . .

EXPOSE $PORT_ARG
CMD [ "npm", "start" ]