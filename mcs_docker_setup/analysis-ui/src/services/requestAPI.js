import axios from 'axios';

console.log("baseUrl", window.API_URL);
const AxiosInstanse = axios.create({
  baseURL: window.API_URL,
  proxyHeaders: false,
  credentials: true,
  crossdomain: true,
  headers: {
    'Content-Type': 'application/json'  
  },
});

const AxiosClient = {
  method: null,
  url: null,
  data: {}
};

export const requestAPI = args => (
  new Promise((resolve, reject) => {
    AxiosClient = {...AxiosClient, ...args};
    AxiosClient.data = args.body;
    AxiosInstanse.request(AxiosClient)
      .then(r => resolve(r))
      .catch(e => reject(e));
  })
);