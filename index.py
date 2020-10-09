from xml.sax import ContentHandler
import xml.sax
import re
import string
import time
from collections import defaultdict 
from collections import Counter
import nltk
nltk.download('stopwords')
from Stemmer import Stemmer
from nltk.corpus import stopwords
from collections import OrderedDict
from pathlib import Path
import os
import bisect

stemmer = Stemmer('porter')
TotalCount=0
WordLimit=10000
FileCount=-1
TotalPage=0
SecondaryList=[]
IndexTable={}
Titles={}
sno = nltk.stem.SnowballStemmer('english')
stop_words = stopwords.words('english')
stopwords_dict = Counter(stop_words)
Mapping ={'title':0,'infobox':1 ,'category':2,'references':3,'external links':4,'body':5}

def split_File(File):
  global WordLimit
  Fcount=0

  FileName="indexfiles/primary"+str(Fcount)+'.txt'
  Primary=open(FileName,"w")

  index=open(File,"r")
  Secondary=open("indexfiles/"+'secondary.txt',"w")

  data = index.readlines() 
  Secondary.write(data[0].split()[0]+"\n")

  count=0
  for line in data: 
    if count == WordLimit:
      Fcount+=1
      Primary.close()
      FileName="indexfiles/primary"+str(Fcount)+'.txt'
      Primary=open(FileName,"w")  
      count=0
      word=line.split()[0]
      Secondary.write(word+"\n")
    Primary.write(line)
    count+=1
  Primary.close()
  Secondary.close()
  index.close()
def storeTitles():
  f=open("indexfiles/titles.txt","w")
  for i in Titles:
    # print(Titles[i])
    f.write(Titles[i]+"\n")
  f.close()
def storePageId():
  global TotalPage
  f=open("indexfiles/PageCount.txt","w")
  f.write(str(TotalPage))
  f.close()
def merge():
  Filename="indexfiles/test_0.txt"
  Count=1
  for count in range(1,FileCount+1):
    Filename=mergeHelper(Filename,Count)
    Count+=1
  split_File(Filename)

def mergeHelper(File1,Count):

  File2 = Path("indexfiles/test_"+str(Count)+".txt")
  # print(File1,File2,Count)  
  
  # if Count==2:
  #   return 
  if File2.is_file()==False:
    return  

  File2=str(File2)

  with open(File1) as f:
    lines_f = [line.rstrip() for line in f]
  with open(File2) as s:
    lines_s = [line.rstrip() for line in s]
  File3="indexfiles/test"+str(Count-1)+str(Count)+".txt"
  m=open(File3,"w")

  i=0 
  j=0
  while i<len(lines_f) and j<len(lines_s):  
    words_f=lines_f[i].split()
    words_s=lines_s[j].split()
    if words_f[0]<words_s[0]:
      m.write(words_f[0]+" ")
      for value in range(1,len(words_f)):
        m.write(words_f[value])
      m.write("\n")
      i+=1
          
    elif words_f[0]==words_s[0]:
      m.write(words_f[0]+" ")
      for value in range(1,len(words_f)):
        m.write(words_f[value])
      for value in range(1,len(words_s)):
        m.write(words_s[value])
      m.write("\n")
      i+=1
      j+=1
    else:
      m.write(words_s[0]+" ")
      for value in range(1,len(words_s)):
        m.write(words_s[value])
      m.write("\n")
      j+=1
  while i<len(lines_f):
    words_f=lines_f[i].split()
    m.write(words_f[0]+" ")
    for value in range(1,len(words_f)):
      m.write(words_f[value])
    m.write("\n")
    i+=1
  while j<len(lines_s):
    words_s=lines_s[j].split()
    m.write(words_s[0]+" ")
    for value in range(1,len(words_s)):
      m.write(words_s[value])
    m.write("\n")
    j+=1

  os.remove(File1)
  os.remove(File2)
  return File3

    

def writeinFile():
  global FileCount
  FileCount+=1
  with open("indexfiles/test_"+str(FileCount)+".txt", "w") as f:  
    for key in sorted(IndexTable):
      f.write(key+' ')
      for subkey in IndexTable[key]:
        f.write(str(subkey))
        lst=IndexTable[key][subkey]
        for i in range(0,len(lst)):
          if i==0 and lst[i]!=0:
            f.write('t'+str(lst[i]))
          if i==1 and lst[i]!=0:
            f.write('i'+str(lst[i]))
          if i==2 and lst[i]!=0:
            f.write('c'+str(lst[i]))
          if i==3 and lst[i]!=0:
            f.write('r'+str(lst[i]))
          if i==4 and lst[i]!=0:
            f.write('e'+str(lst[i]))
          if i==5 and lst[i]!=0:
            f.write('b'+str(lst[i]))
        f.write('|')        
      f.write('\n')

def getIndexTable():
  with open("file.txt", "w") as f:
    data = file.readlines() 
    for line in data: 
        words = line.split()
        IndexTable[words[0]]={}
        for i in range(1,len(words)):
          words[i]

def getTokens(text,PageId,field):
  global TotalCount
  global WordLimit
  Tokens=re.split(r'[^A-Za-z0-9]+',text)
  for word in Tokens:
    if len(IndexTable) == WordLimit:
      writeinFile()
      IndexTable.clear()
    word=stemmer.stemWord(word)    
    count=[0,0,0,0,0,0]
    
    if word not in stopwords_dict and len(word)>2 :
      if word.isdigit() and len(word)>4:
        continue
      count[Mapping[field]] += 1
      TotalCount+=1
      if word not in IndexTable:
        IndexTable[word]={}
        IndexTable[word][PageId]=count
      else:
        if PageId not in IndexTable[word]:
          count[Mapping[field]]+=1
          IndexTable[word][PageId]=count;
        else: 
          IndexTable[word][PageId][Mapping[field]]+=1

def indexStat():
  with open("invertedindex_stat.txt", "w") as f:
    f.write(str(TotalCount)+'\n')
    f.write(str(len(IndexTable)))
      
def getInfo(text,PageId,PageTitle):
  text = text.lower()
  InfoPattern = r'{{infobox(.*?)}}'
  RemoveInfo=re.compile(InfoPattern,re.S)
  Info =re.finditer(InfoPattern, text,re.S)
  
  for line in Info:
    getTokens(line.group(0),PageId,'infobox')
  text=RemoveInfo.sub('',text)
  CategoryPattern=r'\[\[category:(.*?)\]\]'
  RemoveCategory=re.compile(CategoryPattern,re.S)
  Category =re.finditer(CategoryPattern,text,re.S)
  
  for line in Category:
    getTokens(line.group(0),PageId,'category')
  text=RemoveCategory.sub('',text)

  RefPattern = r'== ?references ?==(.*?)=='
  RemoveRef=re.compile(RefPattern,re.S)
  Ref = re.finditer(RefPattern,text,re.S)
  
  for line in Ref:
    getTokens(line.group(0),PageId,'references')
  text=RemoveRef.sub('',text)
  ExPattern=r'== external links ==(.*?)=='
  RemoveEx=re.compile(ExPattern,re.S)
  Ex=re.finditer(ExPattern,text,re.S)
  
  for line in Ex:
    getTokens(line.group(0),PageId,'external links')
  text=RemoveEx.sub('',text)
  PageTitle=PageTitle.lower()
  getTokens(PageTitle,PageId,'title')
  
  getTokens(text,PageId,'body')

class Index(ContentHandler):
  
  def __init__(self):
    self.CurrentTag=""
    self.PageCount = 0
    self.PageText = ""
    self.PageTitle = ""

  def startElement(self,tag,attributes):
    global TotalPage
    self.CurrentTag=tag
    if tag == "page":
      self.PageCount += 1
      TotalPage+=1

    if tag == "text":
      self.Text = ""
      
    
    
  def endElement(self,tag):
    if tag == 'text':
      getInfo(self.PageText,self.PageCount,self.PageTitle)
    self.CurrentTag=""
    self.PageText="" 
    if tag == "title":
      # print(self.PageTitle)
      Titles[self.PageCount]=self.PageTitle;

            
  def characters(self,content):
    if self.CurrentTag=='title':
      self.PageTitle=content
    if self.CurrentTag=='text':
      self.PageText+=content
      

if ( __name__ == "__main__"):
  start_time = time.clock()
  # create an XMLReader
  parser = xml.sax.make_parser()
  # turn off namepsaces
  parser.setFeature(xml.sax.handler.feature_namespaces, 0)

  # override the default ContextHandler
  Handler = Index()
  parser.setContentHandler( Handler)   
  if not os.path.exists("indexfiles"):
    os.mkdir("indexfiles")
  # parser.parse('short.xml')
  
  parser.parse('enwiki-20200801-pages-articles-multistream1.xml-p1p30303')
  parser.parse('enwiki-20200801-pages-articles-multistream2.xml-p30304p88444')
  
  writeinFile() 
  # indexStat()
  storeTitles()
  merge()
  storePageId()
  print (time.clock() - start_time, "seconds")   