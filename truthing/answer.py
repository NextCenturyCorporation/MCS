from collections import defaultdict


class Answer:

    def __init__(self):
        self.answer = self.get_empty_answer()

    def get_answer(self):
        return self.answer

    def get_empty_answer(self):
        answer = self.nested_dict(3, float)
        for block in range(0, 3):
            for test in range(0, 1080):
                for scene in range(4):
                    block_name = str(block + 1)
                    test_name = str(test + 1)
                    scene_name = str(scene + 1)
                    answer[block_name][test_name][scene_name] = -1
        self.answer = answer
        return answer

    def next_test(self, block):
        """Determine the next test that is not -1"""
        for test in range(0, 1080):
            test_name = str(test + 1).zfill(4)
            if self.answer[block][test_name]['1'] == -1:
                return test + 1

        return 1

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
        self.answer = answer
        return answer

    def write_answer_file(self, filename):
        with open(filename, 'w') as outfile:
            for block in range(0, 3):
                for test in range(0, 1080):
                    for scene in range(4):
                        block_name = str('O' + str(block + 1))
                        test_name = str(test + 1).zfill(4)
                        scene_name = str(scene + 1)
                        if block_name in self.answer and test_name in self.answer[block_name] and scene_name in \
                                self.answer[block_name][test_name]:
                            val = int(self.answer[block_name][test_name][scene_name])
                            outfile.write("{}/{}/{} {}\n".format(block_name, test_name, scene_name, val))
                        else:
                            outfile.write("{}/{}/{} -1\n".format(block_name, test_name, scene_name))

    def set_vals(self, block, test, vals):
        self.answer[block][test]['1'] = vals[0]
        self.answer[block][test]['2'] = vals[1]
        self.answer[block][test]['3'] = vals[2]
        self.answer[block][test]['4'] = vals[3]

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
