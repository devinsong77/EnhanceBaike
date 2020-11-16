from LAC import LAC


class LACManager:

    def __init__(self):
        self.lac = LAC(mode='lac')
        self.labels = ['PER', 'LOC', 'ORG']

    def predict(self, words):
        try:
            lac_result = self.lac.run(words)
            res_labels = lac_result[1]
            switch = {
                "PER": '人物',
                "LOC": '地点',
                "ORG": '组织',
            }

            if res_labels[0] in self.labels:
                return switch[res_labels[0]]
            else:
                return '其他'
        except Exception:
            return '其他'
