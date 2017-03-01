# Training part
import math
import numpy as np

class Hmm:
    def __init__(self):
        self.arc = {}
        self.tag_word = {}
        self.dictionary = {}
        self.word_tag = {}
        self.tags_sum = {}
        self.trans_mat = np.zeros(())
        self.emit_mat = np.zeros(())
        self.suffix_matrix = {}
        self.suffix_number = {}
        self.suffixs = []
        self.suffix_probability = {}

        self.tags = []
        self.tags_index = {}
        self.word_index = {}
        self.tokens = []

    def train(self,filename):
        previous_state = ''
        with open(filename) as fp:
            for line in fp:
                if line.strip() != "":
                    items = line.rstrip('\n').split('\t')
                    word = items[0]
                    tag = items[1]
                    if word not in self.dictionary:
                        self.dictionary[word] = 1
                    else:
                        self.dictionary[word] += 1
                    if tag not in self.tags_sum:
                        self.tags_sum[tag] = 1
                    else:
                        self.tags_sum[tag] += 1
                    if word not in self.word_tag:
                        self.word_tag[word] = {}
                        self.word_tag[word][tag] = 1
                    elif word in self.word_tag and tag not in self.word_tag[word]:
                        self.word_tag[word][tag] = 1
                    elif word in self.word_tag and tag in self.word_tag[word]:
                        self.word_tag[word][tag] += 1
                    if previous_state == "":
                        if 'START' not in self.tags_sum:
                            self.tags_sum['START'] = 1
                        else:
                            self.tags_sum['START'] += 1
                        if 'START' not in self.arc:
                            self.arc['START'] = {}
                            self.arc['START'][tag] = 1
                        elif 'START' in self.arc and tag not in self.arc['START']:
                            self.arc['START'][tag] = 1
                        elif 'START' in self.arc and tag in self.arc['START']:
                            self.arc['START'][tag] += 1
                    else:
                        if previous_state not in self.arc:
                            self.arc[previous_state] = {}
                            self.arc[previous_state][tag] = 1
                        elif previous_state in self.arc and tag not in self.arc[previous_state]:
                            self.arc[previous_state][tag] = 1
                        elif previous_state in self.arc and tag in self.arc[previous_state]:
                            self.arc[previous_state][tag] += 1

                    previous_state = tag
                    if tag not in self.tag_word:
                        self.tag_word[tag] = {}
                        self.tag_word[tag][word] = 1
                    elif tag in self.tag_word and word not in self.tag_word[tag]:
                        self.tag_word[tag][word] = 1
                    elif tag in self.tag_word and word in self.tag_word[tag]:
                        self.tag_word[tag][word] += 1
                else:
                    if previous_state != "":
                        if 'END' not in self.tags_sum:
                            self.tags_sum['END'] = 1
                        else:
                            self.tags_sum['END'] += 1
                        if previous_state not in self.arc:
                            self.arc[previous_state] = {}
                            self.arc[previous_state]['END'] = 1
                        elif previous_state in self.arc and 'END' not in self.arc[previous_state]:
                            self.arc[previous_state]['END'] = 1
                        else:
                            self.arc[previous_state]['END'] += 1
                        previous_state = ""

        self.tags = sorted(self.tags_sum.keys())
        start_index = self.tags.index('START')

        self.tags[0],self.tags[start_index] =  self.tags[start_index],self.tags[0]
        end_index = self.tags.index('END')
        self.tags[end_index],self.tags[len(self.tags) - 1] = self.tags[len(self.tags) - 1], self.tags[end_index]
        for i in range(len(self.tags)):
            self.tags_index[self.tags[i]] = i

        self.tokens = sorted(self.dictionary.keys())
        for i in range(len(self.tokens)):
            self.word_index[self.tokens[i]] = i

        self.trans_mat = np.zeros((len(self.tags),len(self.tags)))
        for i in range(len(self.tags)):
            if self.tags[i] not in self.arc:
                for j in range(len(self.tags)):
                    self.trans_mat[i][j] = 0
            else:
                for j in range(len(self.tags)):
                    if self.tags[j] in self.arc[self.tags[i]]:
                        self.trans_mat[i][j] = self.arc[self.tags[i]][self.tags[j]] / self.tags_sum[self.tags[i]]


        self.emit_mat = np.zeros((len(self.tags),len(self.tokens)))

        for tag, word_count in self.tag_word.items():
            for word, count in word_count.items():
                self.emit_mat[self.tags_index[tag]][self.word_index[word]] = count / self.tags_sum[tag]

        np.savetxt('emit_mat.txt',self.emit_mat,delimiter=',')
        np.savetxt('ttrans_mat.txt',self.trans_mat,delimiter=',')


        # self.suffix_matrix = {}
        # for token in self.tokens:
        #     #if dictionary[token] <= 10:
        #         if len(token) <= 10:
        #             if token not in self.suffix_matrix:
        #                 self.suffix_matrix[token] = {}
        #                 for key,value in self.word_tag[token].items():
        #                     self.suffix_matrix[token][key] = value
        #             elif token in self.suffix_matrix:
        #                 for key,value in word_tag[token].items():
        #                     if key not in self.suffix_matrix[token]:
        #                         self.suffix_matrix[token][key] = 0
        #                     self.suffix_matrix[token][key] += value
        #             for i in range(1,len(token)):
        #                 suffix = token[i:]
        #                 if suffix not in self.suffix_matrix:
        #                     self.suffix_matrix[suffix] = self.suffix_matrix[token]
        #                 elif suffix in self.suffix_matrix:
        #                     for key,value in self.word_tag[token].items():
        #                         if key not in self.suffix_matrix[suffix]:
        #                             self.suffix_matrix[suffix][key] = 0
        #                         self.suffix_matrix[suffix][key] += value
        #         else:
        #             suffix_complete = token[len(token) - 10:len(token) - 1]
        #             if suffix_complete not in self.suffix_matrix:
        #                 self.suffix_matrix[suffix_complete] = {}
        #                 for key,value in word_tag[token].items():
        #                     self.suffix_matrix[suffix_complete][key] = value
        #             elif suffix_complete in self.suffix_matrix:
        #                 for key,value in word_tag[token].items():
        #                     if key not in self.suffix_matrix[suffix_complete]:
        #                         self.suffix_matrix[suffix_complete][key] = 0
        #                     self.suffix_matrix[suffix_complete][key] += value
        #             for i in range(1,len(suffix_complete)):
        #                 suffix = suffix_complete[i:]
        #                 if suffix not in self.suffix_matrix:
        #                     self.suffix_matrix[suffix] = self.suffix_matrix[suffix_complete]
        #                 elif suffix in self.suffix_matrix:
        #                     for key,value in self.word_tag[token].items():
        #                         if key not in self.suffix_matrix[suffix]:
        #                             self.suffix_matrix[suffix][key] = 0
        #                         self.suffix_matrix[suffix][key] += value
        #
        # self.suffixs = sorted(self.suffix_matrix.keys())
        # for suffix in self.suffixs:
        #     total = 0
        #     for key,value in self.suffix_matrix[suffix].items():
        #         total += value
        #     self.suffix_number[suffix] = total
        #
        # for suffix in self.suffixs:
        #     self.suffix_probability[suffix] = {}
        #     for tag,value in self.suffix_matrix[suffix].items():
        #         self.suffix_probability[suffix][tag] = value / self.suffix_number[suffix]


##  test part




    def viterbi (self,observations):
        N = len(self.tags) - 2
        T = len(observations)
        viterbi_mat = np.zeros((N+2,T))
        backpointer_mat = np.zeros((N+2,T))

        for s in range(1,N + 1):
            if observations[0] in self.word_index:
                viterbi_mat[s][0] = self.trans_mat[0][s]*self.emit_mat[s][self.word_index[observations[0]]]
            else:
                viterbi_mat[s][0] = self.trans_mat[0][s] * 1 / N

        for t in range(1,T):
            for s1 in range(1,N + 1):
                for s2 in range(1,N + 1):
                    if observations[t] in self.word_index:
                        temp = viterbi_mat[s2][t-1] * self.trans_mat[s2][s1] * self.emit_mat[s1][self.word_index[observations[t]]]
                    else:
                        temp = viterbi_mat[s2][t - 1] * self.trans_mat[s2][s1] * 1 / N
                    if temp > viterbi_mat[s1][t]:
                        viterbi_mat[s1][t] = temp
                        backpointer_mat[s1][t] = s2

        for s in range(1,N+1):
            temp = viterbi_mat[s][T-1] * self.trans_mat[s][N+1]
            if temp > viterbi_mat[N+1][T-1]:
                viterbi_mat[N + 1][T-1] = temp
                backpointer_mat[N+1][T-1] = s

        res = []
        end_state = int(backpointer_mat[N+1][T-1])
        end_word = T - 1
        while end_word >= 0:
            res.append(self.tags[end_state])
            end_state = int(backpointer_mat[end_state][end_word])
            end_word -= 1
        res.reverse()
        np.savetxt('viterbi_mat.txt',viterbi_mat,delimiter=',')
        return res

    def test(self):
        is_sentence = False
        observations = []
        test_res = open('wsj_24.pos','w')
        with open('WSJ_24.words') as fp:
            for line in fp:
                if line.strip() == '':
                    if not is_sentence:
                        continue
                    else:
                        res = self.viterbi(observations)
                        for i in range(len(observations)):
                            test_res.write(observations[i] + '\t' + res[i])
                            test_res.write('\n')
                        observations = []
                        test_res.write('\n')
                else:
                    observations.append(line.rstrip())
                    is_sentence = True

hmm = Hmm()
hmm.train('WSJ_02-21.pos')
hmm.test()
## unknown word
# tags_probability = []
# tags_total_number = sum(tags_sum) - tags_sum[0]
#
# for i in range(len(tags)):
#     if tags[i] == 'START' or tags[i] == 'END':
#         tags_probability.append(0)
#     else:
#         tags_probability.append(tags_sum[i] / tags_total_number)
#
# tags_probability_average = sum(tags_probability) / (len(tags_probability) - 2)
# theta = 0
# for i in range(1,len(tags_probability) - 1):
#     theta += pow((tags_probability[i] - tags_probability_average),2)
# theta = theta / (len(tags_probability) - 3)
