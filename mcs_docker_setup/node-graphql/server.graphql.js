
const {ElasticSearchClient, ElasticSaveClient} = require('./server.elasticsearch');
const elasticSearchSchema = require('./server.es.schema');
const {makeExecutableSchema} = require('graphql-tools');
const _ = require('lodash');
const GraphQLJSON = require('graphql-type-json');
const {performance} = require('perf_hooks');

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
    location_frame: Float
    location_x: Float
    location_y: Float
  }

  type Comment {
    id: String
    block: String
    performer: String
    submission: String
    test: String
    createdDate: String
    text: String
    userName: String
  }

  type Bucket {
    key: String
    doc_count: Float
  }

  type SubmissionBucket {
    key: SubmissionPerformer
    doc_count: Float
  }

  type SubmissionPerformer {
    performer: String
    submission: String
  }

  type Query {
    msc_eval: [Source]
    getEvalByTest(test: String) : [Source]
    getEvalByBlock(block: String) : [Source]
    getEvalBySubmission(submission: String) : [Source]
    getEvalByPerformer(performer: String) : [Source]
    getEvalAnalysis(test: String, block: String, submission: String, performer: String) : [Source]
    getComments(test: String, block: String, submission: String, performer: String) : [Comment]
    getFieldAggregation(fieldName: String) : [Bucket]
    getSubmissionFieldAggregation: [SubmissionBucket]
  }

  type Mutation {
    saveComment(test: String, block: String, submission: String, performer: String, createdDate: String, text: String, userName: String) : Comment
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

function getFieldAggregationSchema(fieldName) {
  return {
      "aggs": {
        "full_name": {
          "terms": {
            "field": fieldName,
            "size": 100000
          }
        }
      },
      "size": 0
  }
}

function getSubmissionFieldAggregationSchema() {
  return {
    "size": 0,
    "aggs" : {
      "full_name": {
        "composite" : {
          "sources" : [
            { "performer": { "terms": {"field": "performer" } } },
            { "submission": { "terms": { "field": "submission" } } } 
          ]
        }
      }
    }
  }
}

// Found function that will generate a UUID to use as a comments ID
function generateUUID() { // Public Domain/MIT
  var d = new Date().getTime(); //Timestamp
  var d2 = (performance && performance.now && (performance.now()*1000)) || 0; //Time in microseconds since page-load or 0 if unsupported
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16;//random number between 0 and 16
      if(d > 0){ //Use timestamp until depleted
          r = (d + r)%16 | 0;
          d = Math.floor(d/16);
      } else { //Use microseconds since page-load if supported
          r = (d2 + r)%16 | 0;
          d2 = Math.floor(d2/16);
      }
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
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
    }),
    getFieldAggregation: (obj, args, context, infow) => new Promise((resolve, reject) => {
      ElasticSearchClient('msc_eval', getFieldAggregationSchema(args["fieldName"]))
        .then(r => {
          let _source = r.body.aggregations.full_name.buckets;
          resolve(_source);
        });
    }),
    getSubmissionFieldAggregation: (obj, args, context, infow) => new Promise((resolve, reject) => {
      ElasticSearchClient('msc_eval', getSubmissionFieldAggregationSchema())
        .then(r => {
          let _source = r.body.aggregations.full_name.buckets;
          resolve(_source);
        });
    })
  }, 
  Mutation: {
    saveComment: async (obj, args, context, infow) => {
      return await ElasticSaveClient('comments', 'comment', {
        id: generateUUID(),
        test: args["test"],
        block: args["block"],
        submission: args["submission"],
        performer: args["performer"],
        text: args["text"],
        createdDate: args["createdDate"],
        userName: args["userName"]
      });
    }
  }
};

module.exports = makeExecutableSchema({
  "typeDefs": [typeDefs],
  "resolvers": resolvers
});