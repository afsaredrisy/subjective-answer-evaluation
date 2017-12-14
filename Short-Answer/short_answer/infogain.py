#ref - https://stackoverflow.com/questions/46752650/information-gain-calculation-with-scikit-learn
#ref - https://stackoverflow.com/questions/43643278/how-do-i-selectkbest-using-mutual-information-from-a-mixture-of-discrete-and-con

from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest
from scipy.sparse import lil_matrix
import numpy as np
import read_data as rd
import csv, os, scipy
import operator
from sklearn.neighbors import KNeighborsClassifier


from sklearn.utils import check_X_y

class SelectKBestCustom(SelectKBest):

    # Changed here
    def fit(self, X, y, discrete_features='auto'):
        X, y = check_X_y(X, y, ['csr', 'csc'], multi_output=True)

        if not callable(self.score_func):
            raise TypeError("The score function should be a callable, %s (%s) "
                        "was passed."
                        % (self.score_func, type(self.score_func)))

        self._check_params(X, y)

        # Changed here also
        score_func_ret = self.score_func(X, y, discrete_features)
        if isinstance(score_func_ret, (list, tuple)):
            self.scores_, self.pvalues_ = score_func_ret
            self.pvalues_ = np.asarray(self.pvalues_)
        else:
            self.scores_ = score_func_ret
            self.pvalues_ = None

        self.scores_ = np.asarray(self.scores_)
        return self

def delete_row_csr(mat, i):
    if not isinstance(mat, scipy.sparse.csr_matrix):
        raise ValueError("works only for CSR format -- use .tocsr() first")
    n = mat.indptr[i+1] - mat.indptr[i]
    if n > 0:
        mat.data[mat.indptr[i]:-n] = mat.data[mat.indptr[i+1]:]
        mat.data = mat.data[:-n]
        mat.indices[mat.indptr[i]:-n] = mat.indices[mat.indptr[i+1]:]
        mat.indices = mat.indices[:-n]
    mat.indptr[i:-1] = mat.indptr[i+1:]
    mat.indptr[i:] -= n
    mat.indptr = mat.indptr[:-1]
    mat._shape = (mat._shape[0]-1, mat._shape[1])




def main(stud_ans):
    n = len(stud_ans)
    target = []
    data = []
    data.extend(stud_ans)
    for i in range(0,n):
        target.extend("0")
    op = rd.read_data("train.tsv")
    data.extend(op[0])
    target.extend(op[1])
    cv = CountVectorizer(max_df=1.0, min_df=2,ngram_range=(1, 2),
                                     max_features=10000,
                                     stop_words='english')
    X_vec = cv.fit_transform(data)
    #print X_vec.shape
    #mutual_info_classif(X_vec, target, discrete_features=True)
    X_new = SelectKBestCustom(mutual_info_classif, k=500).fit_transform(X_vec, target)
    #print X_new.shape
    q = X_new.shape[1]
    #X_test = [[0 for x in range(m)] for y in range(n)]
    X_test = lil_matrix((n,q)) 
    for i in range(0,n):
        X_test[i] = X_new[i]
    for i in range(0,n):
        delete_row_csr(X_new, i)
        del target[i]
    knn = KNeighborsClassifier(n_neighbors=1, algorithm='brute', metric='cosine')
    knn.fit(X_new, target)
    #print X_test
    # Classify the test vectors.
    p = knn.predict(X_test)
    #float(p[0])
    #print "infogain", p[0]
    return p

   
if __name__ == "__main__":
    stud_ans = raw_input("Enter answer: ")
    main([stud_ans])