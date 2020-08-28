import React from "react";
import ReactDOM from "react-dom";
import { App } from "./components/App";

import { ApolloProvider } from 'react-apollo'
import { ApolloClient } from 'apollo-client'
import { createHttpLink } from 'apollo-link-http'
import { InMemoryCache } from 'apollo-cache-inmemory'

console.log("uri", window.GRAPHQL_URL, "1002");

const httpLink = createHttpLink({
  uri: window.GRAPHQL_URL
});

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache()
});

ReactDOM.render(
  <ApolloProvider client={client}><App /></ApolloProvider>,
  document.getElementById("root")
);