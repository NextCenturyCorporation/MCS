/* Generic Elastic Schema that will return all entries in Elastic */
module.exports = {
    "size": 1000,
    "from": 0,
    "query": {
      "match_all": {}
    }
  };