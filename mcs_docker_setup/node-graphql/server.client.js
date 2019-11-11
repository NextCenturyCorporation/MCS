const ElasticSearch = require('elasticsearch');
const { Client: Client6 } = require('es6');

/**
 * *** ElasticSearch *** client
 * @type {Client}
 */
const hostName = process.env.ELASTIC_URL || "http://localhost:9200";

// const client = new ElasticSearch.Client({
//   hosts: [hostName]
// });

const client = new Client6({ node: hostName })

module.exports = client;
