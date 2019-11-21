
const {ElasticSearchClient, ElasticSaveClient} = require('./server.elasticsearch');
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

  type Comment {
    block: String
    performer: String
    submission: String
    test: String
    createdDate: String
    text: String
  }

  type Query {
    msc_eval: [Source]
    getEvalByTest(test: String) : [Source]
    getEvalByBlock(block: String) : [Source]
    getEvalBySubmission(submission: String) : [Source]
    getEvalByPerformer(performer: String) : [Source]
    getEvalAnalysis(test: String, block: String, submission: String, performer: String) : [Source]
    getComments(test: String, block: String, submission: String, performer: String) : [Comment]
  }

  type Mutation {
    saveComment(test: String, block: String, submission: String, performer: String, createdDate: String, text: String) : Comment
  }
`;

/* Create a generic elastic search query schema for one field */
function getElasticSchema(fName, fieldValue) {
  const matchObj = {};
  matchObj[fName] = fieldValue;
  return {
      "size": 1000,
      "from": 0,
      "query": {
        "match": matchObj
      }
    };
}

function getAnalysisSchema(testVal, blockVal, submissionVal, perfomerVal) {
  return {
    "query": {
      "bool": {
        "must": [
          {"match": {"test": testVal}},
          {"match": {"block": blockVal}},
          {"match": {"submission": submissionVal}},
          {"match": {"performer": perfomerVal}}
        ]
      }
    }
  };
}

// The root provides a resolver function for each API endpoint
const resolvers = {
  Query: {
    msc_eval: (obj, args, context, infow) => new Promise((resolve, reject) => {
      ElasticSearchClient('msc_eval', {...elasticSearchSchema})
        .then(r => {
          let _source = r.body.hits.hits;
              _source.map((item, i) => _source[i] = item._source);
          resolve(_source);
        });
    }),
    getEvalByTest: (obj, args, context, infow) => new Promise((resolve, reject) => {
      ElasticSearchClient('msc_eval', getElasticSchema("test", args["test"]))
        .then(r => {
          let _source = r.body.hits.hits;
              _source.map((item, i) => _source[i] = item._source);
          resolve(_source);
        });
    }),
    getEvalByBlock: (obj, args, context, infow) => new Promise((resolve, reject) => {
      ElasticSearchClient('msc_eval', getElasticSchema("block", args["block"]))
        .then(r => {
          let _source = r.body.hits.hits;
              _source.map((item, i) => _source[i] = item._source);
          resolve(_source);
        });
    }),
    getEvalBySubmission: (obj, args, context, infow) => new Promise((resolve, reject) => {
      ElasticSearchClient('msc_eval', getElasticSchema("submission", args["submission"]))
        .then(r => {
          let _source = r.body.hits.hits;
              _source.map((item, i) => _source[i] = item._source);
          resolve(_source);
        });
    }),
    getEvalByPerformer: (obj, args, context, infow) => new Promise((resolve, reject) => {
      ElasticSearchClient('msc_eval', getElasticSchema("performer", args["performer"]))
        .then(r => {
          let _source = r.body.hits.hits;
              _source.map((item, i) => _source[i] = item._source);
          resolve(_source);
        });
    }),
    getEvalAnalysis: (obj, args, context, infow) => new Promise((resolve, reject) => {
      ElasticSearchClient('msc_eval', getAnalysisSchema(args["test"], args["block"], args["submission"], args["performer"]))
        .then(r => {
          let _source = r.body.hits.hits;
              _source.map((item, i) => _source[i] = item._source);
          resolve(_source);
        });
    }),
    getComments: (obj, args, context, infow) => new Promise((resolve, reject) => {
      ElasticSearchClient('comments', getAnalysisSchema(args["test"], args["block"], args["submission"], args["performer"]))
        .then(r => {
          let _source = r.body.hits.hits;
              _source.map((item, i) => _source[i] = item._source);
          resolve(_source);
        });
    })
  }, 
  Mutation: {
    saveComment: async (obj, args, context, infow) => {
      return await ElasticSaveClient('comments', 'comment', {
        test: args["test"],
        block: args["block"],
        submission: args["submission"],
        performer: args["performer"],
        text: args["text"],
        createdDate: args["createdDate"]
      });
    }
  }
};

module.exports = makeExecutableSchema({
  "typeDefs": [typeDefs],
  "resolvers": resolvers
});