#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019 Next Century Corporation 
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Read in submission, metadata, and ground truth to create an elastic search 
index that can be read by Neon.

"""
import json
import zipfile
from pathlib import Path
import os
import io
from elasticsearch import Elasticsearch
from collections import defaultdict

config = {
    'elastic_host': 'localhost',
    'elastic_port': 9200,
    'index_name': 'msc_eval',
    'index_type': 'eval1'
}

settings = '''
        {
          "settings": {
            "number_of_shards": "1",
            "number_of_replicas": "0"
          },
          "mappings": {
            "eval1": {
              "properties": {
                "performer": {
                  "type": "keyword"
                },
                "submission": {
                  "type": "keyword"
                },              
                "block": {
                  "type": "keyword"
                },
                "test": {
                  "type": "keyword"
                },
                "scene": {
                  "type": "keyword"
                },
                "num_objects": {
                  "type": "keyword"
                },
                "complexity": {
                  "type": "keyword"
                },
                "occluder": {
                  "type": "keyword"
                },
                "ground_truth": {
                  "type": "double"
                },
                "plausibility": {
                  "type": "double"
                },
                "url_string": {
                  "type": "keyword"
                }
              }
            }
          }
        }
        '''


class JsonImportCreator:

    def __init__(self):

        # global counter
        self.object_id = 0

        # Performer data
        # self.sub_file = "submission_example.zip"

        # Find all the submission data
        self.submission_files = [f for f in os.listdir('.') if
                                 str(f).startswith("submission_") and str(f).endswith(".zip")]
        self.submission_files.sort()
        self.answer_filename = "answer.txt"
        self.description_filename = "description.json"

        # Test data
        self.metadata_filename = "metadata.json"
        self.ground_truth_filename = "ground_truth.txt"

        # connect to es
        self.es = Elasticsearch([{'host': config['elastic_host'], 'port': config['elastic_port']}])

        # delete index if exists
        if self.es.indices.exists(config['index_name']):
            print("Removing existing index")
            self.es.indices.delete(index=config['index_name'])

        # create index
        self.es.indices.create(index=config['index_name'], ignore=400, body=settings)

    def process(self):
        # Get the metadata
        self.metadata = self.get_metadata()
        # print(" metadata {}".format(self.metadata))

        # Get the ground truth data
        self.ground_truth = self.get_ground_truth()

        for file in self.submission_files:
            print("Submission file: {}".format(file))
            self.process_submission(file)

    def process_submission(self, filename):

        # Get the submission data description
        description = self.get_description_information(filename)
        answer = self.get_answer(filename)
        voe_signal = self.get_voe_signal(filename)
        print("voe signal {}".format(voe_signal))

        bulk_data = []

        for block in answer:
            for test in answer[block]:
                for scene in answer[block][test]:
                    # print("block {} test {} scene {}: score {}".
                    #   format(block, test, scene, answer[block][test][scene]))

                    # Get the dictionary entry
                    op_dict = {
                        "index": {
                            "_index": config['index_name'],
                            "_type": config['index_type'],
                            "_id": self.object_id
                        }
                    }
                    bulk_data.append(op_dict)

                    # Get the data
                    data_dict = {}

                    url_string = "perf={}&subm={}&block={}&test={}".format(description["Performer"],
                                                                           description["Submission"], block, test)

                    # Data associated with the performer
                    data_dict["performer"] = description["Performer"]
                    data_dict["submission"] = description["Submission"]
                    data_dict["block"] = block
                    data_dict["test"] = test
                    data_dict["scene"] = scene

                    # Data associated with this test
                    data_dict["num_objects"] = self.metadata[block][test]["num_objects"]
                    data_dict["complexity"] = self.metadata[block][test]["complexity"]
                    data_dict["occluder"] = self.metadata[block][test]["occluder"]

                    data_dict["ground_truth"] = self.ground_truth[block][test][scene]

                    # Data associated with performer results
                    data_dict["plausibility"] = answer[block][test][scene]
                    data_dict["voe_signal"] = voe_signal[block][test][scene]
                    data_dict["url_string"] = url_string
                    bulk_data.append(data_dict)

                    self.object_id = self.object_id + 1

        res = self.es.bulk(index=config['index_name'], body=bulk_data, refresh=True)
        # print("Result: {}".format(res))

    def get_metadata(self):
        with open(self.metadata_filename) as metadata_file:
            metadata = json.load(metadata_file)
            return metadata
        # Handle case where this did not work

    def get_ground_truth(self):
        with open(self.ground_truth_filename) as ground_truth_file:
            return self.parse_answer_file(ground_truth_file)
        print("Unable to get file {}".format(self.ground_truth_filename))

    def get_answer(self, filename):
        """ Pull the answer.txt file out of a zipfile and return parsed object"""
        with zipfile.ZipFile(filename) as my_zip:
            content = my_zip.namelist()
            if self.answer_filename in content:
                with my_zip.open(self.answer_filename) as answer_file:
                    return self.parse_answer_file(answer_file)
        print("Unable to get file {}".format(self.answer_filename))

    def parse_answer_file(self, file):
        """ Parse an answer.txt or ground_truth.txt file, looks like:
        O1/0001/1 1
        O1/0001/2 0
        O1/0001/3 0
        O1/0001/4 1
        ....
        """
        answer = self.nested_dict(3, float)
        for line in file:
            # The following is necessary because what we get from a regular file and a zip file are different
            if isinstance(line, (bytes, bytearray)):
                line = line.decode('utf-8')
            split_line = line.split()
            if len(split_line) != 2:
                raise ValueError('lines must have 2 fields, line {} has {}'.format(line, len(split_line)))

            # Line looks like:  O3/1076/2 1
            first_part = split_line[0]
            key = first_part.split('/')
            block = str(key[0])
            test = str(key[1])
            scene = str(key[2])
            # print("{} {} {} {}".format(block, test, scene, split_line[1]))
            answer[block][test][scene] = float(split_line[1])
        return answer

    def get_description_information(self, filename):
        """ Pull the description.txt file out of a zip and read in the information"""
        with zipfile.ZipFile(filename) as my_zip:
            content = my_zip.namelist()
            if self.answer_filename in content:
                with my_zip.open(self.description_filename, 'r') as description_file:

                    #  d = io.TextIOWrapper(description_file)
                    #  description = json.load(d)

                    description = json.load(description_file)
                    return description
        # Handle case where this did not work

    def get_voe_signal(self, filename):
        voe_signal = self.nested_dict(4,float)
        with zipfile.ZipFile(filename) as my_zip:
            voe_content = [f for f in my_zip.namelist() if str(f).startswith("voe_")]
            for voe_filename in voe_content:

                key = voe_filename.split('_')
                block = str(key[1])
                test = str(key[2])
                scene = str(key[3]).split('.')[0]

                with my_zip.open(voe_filename) as voe_file:
                    for cnt, line in enumerate(voe_file):
                        if isinstance(line, (bytes, bytearray)):
                            line = line.decode('utf-8')
                        split_line = line.split(' ')
                        val = float(split_line[1])
                        voe_signal[block][test][scene][str(cnt+1)] = val
        return voe_signal

    def check(self):
        # sanity check
        res = self.es.search(index=config['index_name'], size=2, body={"query": {"match_all": {}}})
        print("Query response: '{}'".format(res))

    def nested_dict(self, n, type):
        """ Create a multi dimensional dictionary of dimension n.
        See: https://stackoverflow.com/questions/29348345/declaring-a-multi-dimensional-dictionary-in-python/39819609
        """
        if n == 1:
            return defaultdict(type)
        else:
            return defaultdict(lambda: self.nested_dict(n - 1, type))


if __name__ == "__main__":
    handler = JsonImportCreator()
    handler.process()
    handler.check()
