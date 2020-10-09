import re
import string
import nltk
nltk.download('stopwords')
from Stemmer import Stemmer
from nltk.corpus import stopwords
from collections import OrderedDict
from pathlib import Path
import os
import bisect
import math
import sys
import nltk
from Stemmer import Stemmer
from collections import Counter

PageCount=0
stemmer = Stemmer('porter')
stop_words = stopwords.words('english')
stopwords_dict = Counter(stop_words)

nltk.download('stopwords')
SecondaryIndex=[]
WordPageFreq={}
WordPageId={}
WordIdf={}
WordTfIdf={}
IdTitles={}
TopKwords=0
stemmer = Stemmer('porter')

def getTitles():
  f=open("indexfiles/titles.txt","r")
  data=f.readlines()
  cnt =1
  for line in data:
    value=line.split()[0]
    if value != "":
      IdTitles[cnt]=value
      cnt=cnt+1
  f.close()
def getPageCount():
  global PageCount
  f=open("indexfiles/PageCount.txt","r")
  PageCount=int(f.readline())
  f.close()
def calculateIdf(Word,field,flag):
  global PageCount
  freq=0
  if Word in WordPageFreq:
    freq=len(WordPageId[Word])
    idf=math.log(PageCount/freq)
    WordIdf[Word]=idf
def getIntersection(lst):
  if len(lst)==0:
    return []
  return set.intersection(*map(set,lst))
def getUnion(lst):
  if len(lst)==0:
    return []
  return set().union(*lst)
def getTfidf(ResultList,field,flag):
  for id in ResultList:
    Tfidf =0
    for word in WordPageFreq:
      if id in WordPageFreq[word].keys():
        Tf=0
        count=WordPageFreq[word][id]
        if count > 0:
          count = 1+math.log(count)
        else: 
          count=0
        Tf=count * WordIdf[word]
        Tfidf+=Tf
      WordTfIdf[id]=Tfidf
  if field=='x':
    getTopKwords() 
def getTopKwords():
  cnt=0
  f=open("queries_op.txt​","a")
  for w in sorted(WordTfIdf, key=WordTfIdf.get, reverse=True):
    if cnt>=TopKwords:
      break 
    cnt+=1
    f.write(str(w)+","+IdTitles[w]+"\n")
  f.write("\n")
  f.close()
def getTopKdocid(WordList):
  f=open("queries_op.txt​","a")
  for w in WordList:
    f.write(str(w)+","+IdTitles[w]+"\n")
  f.write("\n")
  f.close()
def nonFieldQuery(text,field,flag):
  WordIdf.clear()
  WordPageFreq.clear()
  WordPageId.clear()
  WordTfIdf.clear()
  text = text.lower();
  Tokens=re.split(r'[^A-Za-z0-9]+',text)
  for word in Tokens:
    if word not in stopwords_dict and len(word)>2 :
      if word.isdigit() and len(word)>4:
        continue
      word =stemmer.stemWord(word)

      PostingList=getPosting(word,field,flag)
      # print(word)
      if PostingList:
        processPostingList(PostingList,word,field,flag)
  WordList=[]
  for word in WordPageFreq:
    calculateIdf(word,field,flag)
    WordList.append(WordPageId[word])
  result=getIntersection(WordList)
  result=list(result)

  if len(result) < TopKwords:
    result=getUnion(WordList)
  getTfidf(result,field,flag)

def processFieldData(text):
  text=text.split()
  SearchData = []
  DataField = []
  value=""
  for word in text:
    if ':' in word:
      if value !="":
        SearchData.append(value)
      Field=word.split(':')[0]
      DataField.append(Field)
      value=word.split(':')[1]
    else:
      value+=" "+word
  if value !="":
    SearchData.append(value)
  # print(SearchData)
  # print(DataField)
  return SearchData,DataField
def check(text):
  
  for i in text: 
    if i==':':
      fieldQuery(text)
      return
  nonFieldQuery(text,'x',False)

def fieldQuery(text):
  SearchData,DataField=processFieldData(text)
  FinalList=[]
  for i in range(0,len(SearchData)):
    CurrentList=[]
    nonFieldQuery(SearchData[i],DataField[i],True)
    cnt=0
    for w in sorted(WordTfIdf, key=WordTfIdf.get, reverse=True):
      if cnt>=TopKwords:
        break 
      CurrentList.append(w)
      cnt+=1
    FinalList.append(CurrentList)
  result=getIntersection(FinalList)
  result=list(result)

  if len(result) < TopKwords:
    result=getUnion(FinalList)
  getTopKdocid(result)




def getPosting(Word,field,flag):
  
  FileId = bisect.bisect(SecondaryIndex, Word)
  if FileId >0:
    FileId = FileId-1 
  f= open("indexfiles/primary" +str(FileId)+".txt", "r")
  PostingList = ""
  for line in f:
    data=line.split()
    if data[0]==Word:
      for i in range(1,len(data)):  
        PostingList+=data[i]
  f.close()
  return PostingList
def processPostingList(PostingList,Word,field,flag):
  WordPageFreq[Word]={}
  Tokens=PostingList.split('|')
  PageList=[]
  for i in Tokens:
    if i=="":
      continue
    PageId=int((re.findall(r'^[0-9]+',i)[0]))
    if PageId not in WordPageFreq[Word]: 
      WordPageFreq[Word][PageId]=0
    PageList.append(PageId)
    
    tlist=[]
    ilist=[]
    clist=[]
    elist=[]
    rlist=[]
    blist=[]

    if field=='t' or field=='x':
      tlist=re.findall(r't[0-9]+',i)
    if field=='i' or field=='x':
      ilist=re.findall(r'i[0-9]+',i)
    if field=='c' or field=='x':    
      clist=re.findall(r'c[0-9]+',i)
    if field=='r' or field=='x':
      rlist=re.findall(r'r[0-9]+',i)
    if field=='e' or field=='x':
      elist=re.findall(r'e[0-9]+',i)
    if field=='b' or field=='x':
      blist=re.findall(r'b[0-9]+',i)
    if tlist:
      WordPageFreq[Word][PageId]+=int(tlist[0][1:])
    if blist:
      WordPageFreq[Word][PageId]+=int(blist[0][1:])
    if clist:
      WordPageFreq[Word][PageId]+=int(clist[0][1:])
    if rlist:
      WordPageFreq[Word][PageId]+=int(rlist[0][1:])
    if elist:
      WordPageFreq[Word][PageId]+=int(elist[0][1:])
    if ilist:
      WordPageFreq[Word][PageId]+=int(ilist[0][1:])
    
  PageList=sorted([*{*PageList}])
  WordPageId[Word]=PageList
def processInput(path):
  f=open(path)
  global TopKwords
  data=f.readlines()
  for line in data:
    # value=line.split(',')
    K=str(re.findall(r'(.*),',line)[0])
    text=re.findall(r', (.*)',line)[0]
    TopKwords=int(K)
    # print(K,text)
    check(text)


if ( __name__ == "__main__"):

  IdTitles.clear()
  f=open("indexfiles/"+"secondary.txt","r")
  SecondaryIndex=f.readlines()
  f.close()
  getTitles()
  getPageCount()
  processInput(sys.argv[1])
