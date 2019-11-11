
const {ElasticSearchClient} = require('./server.elasticsearch');
const elasticSearchSchema = require('./server.es.schema');
const {makeExecutableSchema} = require('graphql-tools');
const _ = require('lodash');
const GraphQLJSON = require('graphql-type-json');

// Construct a schema, using GraphQL schema language
const typeDefs = `
  scalar JSON

  type Source {
    block: String
    complexity: String
    ground_truth: Float
    num_objects: String
    occluder: String
    performer: String
    plausibility: Float
    scene: String
    submission: String
    test: String
    url_string: String
    voe_signal: JSON
  }

  type Query {
    msc_eval: [Source]
  }
`;

// The root provides a resolver function for each API endpoint
const resolvers = {
  Query: {
    msc_eval: () => new Promise((resolve, reject) => {
      ElasticSearchClient({...elasticSearchSchema})
        .then(r => {
          let _source = r.body.hits.hits;
              _source.map((item, i) => _source[i] = item._source);
          resolve(_source);
        });
    }),
  }
};

module.exports = makeExecutableSchema({
  "typeDefs": [typeDefs],
  "resolvers": resolvers
});