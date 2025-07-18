# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 15:39:03 2025

@author: aeverman
"""

from datetime import datetime
import time
intervals = []
def test():
    t1 = datetime.now()
    for i in range(100):
        time.sleep(0.01)
        t2 = datetime.now()
        intervals.append(t2-t1)
        #t1 = t2
test()