
# coding: utf-8

# In[ ]:

#import packages needed for model building


# In[ ]:

def predict_pts(date):
    return 25
def predict_rbs(date):
    return 10
def predict_ast(date):
    return 9


# In[ ]:

class prediction:
    
    def __init__(self,date):
        self.pts = predict_pts(date)
        self.rbs = predict_rbs(date)
        self.ast = predict_ast(date)

