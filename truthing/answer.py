from collections import defaultdict


class Answer:

    def __init__(self, file):
        self.answer = self.parse_answer_file(file)

    def get_answer(self):
        return self.answer

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

    def print_answer(self):
        for block in self.answer.keys():
            for test in self.answer[block].keys():
                print("{}".format(self.answer[block][test].values()))

    def nested_dict(self, n, type):
        """ Create a multi dimensional dictionary of dimension n.
        See: https://stackoverflow.com/questions/29348345/declaring-a-multi-dimensional-dictionary-in-python/39819609
        """
        if n == 1:
            return defaultdict(type)
        else:
            return defaultdict(lambda: self.nested_dict(n - 1, type))
