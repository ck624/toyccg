# -*- coding:utf-8 -*-
import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)) , ".." , "toyccg"))
from ccgparser import *
from tree import *


#-- special combinator for Japanese
def FwdRel(lt,rt):
    if rt!=Symbol("N"):
       return None
    if lt==Symbol("S[null]") or lt==Symbol("S") or lt==[BwdApp , [BwdApp , Symbol("S") , Symbol("NP[sbj]")] , Symbol("NP[obj]")]:
       return Symbol("N")
    return None


jp_combinators = [LApp,RApp,LB,RB,LS,RS,RSx,Conj,FwdRel]
jp_terminators = ["ROOT","S","S[exc]","S[imp]","S[null]","S[q]","S[null-q]","S[nom]"]

def jptest(sentence,lexicon,type=0):
   def decode(left_start , right_end , path , chart):
       ret = []
       if len(path)==1:
          return ret
       elif len(path)==3:
          idx = path[0]
          cat1,path1 = chart[(left_start,right_end)][idx]
          if len(path1)==0:
              return [(left_start , right_end , cat1)]
          else:
              return decode(left_start,right_end , path1 , chart)
       else:
          assert(len(path)==5),path
          idx1,idx2,left_end,_,_ = path
          right_start = left_end+1
          cat1,path1 = chart[(left_start,left_end)][idx1]
          cat2,path2 = chart[(right_start,right_end)][idx2]
          if len(path1)==1:
              ret.append( (left_start,left_end,cat1) )
          else:
              ret.extend( decode(left_start,left_end , path1 , chart) )
          if len(path2)==1:
              ret.append( (right_start,right_end,cat2) )
          else:
              ret.extend( decode(right_start,right_end ,path2, chart) )
          return ret
   def decode2(left_start , right_end , path , chart):
       if len(path)==0+1:
          return "".join(sentence[left_start:right_end+1])
       elif len(path)==2+1:
          idx = path[0]
          cat1,path1 = chart[(left_start,right_end)][idx]
          child = decode2(left_start,right_end , path1 , chart)
          if type(child)==unicode:
             return Leaf(catname(cat1) , child)
          else:
             return Tree(path[1] , child)
       else:
          assert(len(path)==4+1),path
          idx1,idx2,left_end,_,_ = path
          right_start = left_end+1
          cat1,path1 = chart[(left_start,left_end)][idx1]
          cat2,path2 = chart[(right_start,right_end)][idx2]
          leftnode = decode2(left_start,left_end , path1 , chart)
          rightnode = decode2(right_start,right_end , path2, chart)
          if not isinstance(leftnode,Tree):
               leftnode = Leaf(catname(cat1) , leftnode)
          if not isinstance(rightnode,Tree):
               rightnode = Leaf(catname(cat2) , rightnode)
          t = Tree(path[3] , leftnode , rightnode)
          return t
#          return (path[3],(catname(cat1),decode2(left_start,left_end , path1 , chart)) , (catname(cat2),decode2(right_start,right_end , path2, chart)))
   print(u"test run : sentence={0}".format(sentence))
   for chart in buildChart(sentence,lexicon,jp_combinators,jp_terminators):
       topcat,path = chart[(0,len(sentence)-1)][-1]
       if type==1:
           print( (topcat.value() , decode(0 , len(sentence)-1 , path , chart)) )
           print("")
       elif type==0:
           for (sidx,eidx,cat) in decode(0 , len(sentence)-1 , path , chart):
               print(u"{0} {1}".format(sentence[sidx:eidx+1] ,catname(cat)))
           break
       else:
           print( unicode(decode2(0 , len(sentence)-1 , path , chart)) )
           break
   print("")



class JPLexicon(object):
    def __init__(self, dic=None):
        self.static_dics = {}
        if dic!=None:
             for line in open(dic, encoding='utf-8'):
                 line = line.strip()
                 if len(line)==0:continue
                 ls = line.split('\t')
                 self.static_dics.setdefault(ls[0],[]).extend( [c for c in ls[1].split(",")] )
    def __getitem__(self,tok):
        w = tok
        cats = self.static_dics.get(w , [])
        ret = []
        for c in cats:
            if not isinstance(c,basestring):
                 ret.append( c )
        for c in set([x for x in cats if isinstance(x,basestring)]):
            ret.append( lexify(c) )
            assert(ret[-1]!=None),("lexicon error:{0}".format(c))
        return ret
    def __setitem__(self,tok,cats):
        self.static_dics[tok] = cats
    def setdefault(self,key,defval):
        if key in self.static_dics:
             return self.static_dics[key]
        else:
             return self.static_dics.setdefault(key,defval)
    def has_key(self,tok):
        return (tok in self.static_dics)
    def get(self,toklist,defval):
        ret = self.__getitem__(toklist)
        return ret




"""
動詞語幹
VP[neg]:未然形
VP[cont]:連用形
VP[euph]:連用形(過去)

S[q]:疑問文
S[imp]:命令文
S[exc]:感嘆文
S[null]:主語が省略された文
S[nom]:体言止め(nominal phrase)


二重ガ格構文:"Xは"の範疇はS/Sである(文を修飾する)と解釈することにする
- 象は鼻が長い => As for an elephant, the nose is long.
- 彼は力は強いが、頭は悪い
- 彼は鼻が利く
- 理由は彼が聞いた
- カキ料理は広島が本場だ
- 酒はロシア人が強い
- 彼の方法は、わたしは嫌いだ。
- 私は朝は体温が高い


助詞の「も」
- 彼も私も、猫を好きだ(主格的)
- 彼も私も、猫が好きだ(主格的)
- 私は、犬も猫も好きだ(目的格的)
- 私は、犬と猫を好きだ
- 私は、犬と猫が好きだ
- 私は、今日も明日も走る(修飾格的)
- 私は、今日と明日に走る
- 私は、今日と明日も走る(修飾格的)
- 彼も私も、彼女は好きだ
- 彼も私も、彼女が好きだ
- 彼女は、彼も私も好きだ
- 彼女が、彼も私も好きだ
- 彼女のことは、彼も私も好きだ


- 私は読書が好きだ
- 読書は私が好きだ
- 私は肉も好きだ
- 私も肉は好きだ
- 肉も私は好きだ
- 肉は私も好きだ

Semantically unpredictable sentences, 合文法無意味文
- 肉は魚も好き
- 魚は肉も好き


"""
if __name__=="__main__":
   TOPDIR = os.path.dirname(os.path.abspath(__file__))
   lexicon = JPLexicon(os.path.join(TOPDIR , "ccglex.jpn"))
   #-- 機能語
   lexicon[u"。"] = ["ROOT\\S","ROOT\\S[null]","ROOT\\S[nom]"]
   lexicon[u"、"] = ["(N/N)\\N" ,[FORALL ,[Symbol("X")] , [BwdApp , Symbol("X") , Symbol("X")]]]
   lexicon[u"たい"] = ["(S\\NP[sbj])\\IV[cont]" , "((S\\NP[sbj])\\NP[obj])\\VP[cont]"]
   lexicon.setdefault(u"的",[]).extend( ["N[adj]\\N" , "(N/N[base])\\N[base]"] )
   lexicon[u"など"] = ["N\\N"]
   #-- (形容詞,非自立)
   lexicon[u"にくい"] = ["(S\\NP[sbj])\\IV[cont]" , "((S\\NP[sbj])\\NP[obj])\\VP[cont]"]
   lexicon[u"やすい"] = ["(S\\NP[sbj])\\IV[cont]" , "((S\\NP[sbj])\\NP[obj])\\VP[cont]"]
   lexicon[u"やすく"] = ["IV[a-cont]\\IV[cont]" , "VP[a-cont]\\VP[cont]"]
   lexicon[u"やすけれ"] = ["IV[a-hyp]\\IV[cont]" , "IV[a-hyp]\\IV[cont]"]
   #--
   lexicon[u"な"] = ["(N/N)\\N[adj]","(N[base]/N[base])\\N[adj]"]
   lexicon[u"は"] = ["NP[sbj]\\N","(S/S)\\N"]
   lexicon[u"が"] = ["NP[sbj]\\N","NP[ga-acc]\\N","(S/S)\\S"]
   lexicon[u"も"] = ["(S/S)\\N","NP[sbj]\\N","NP[nom-enum]\\N","(NP[sbj]/NP[nom-enum])\\N","(NP[nom-enum]/NP[nom-enum])\\N"]
   lexicon[u"を"] = ["NP[obj]\\N"]
   lexicon[u"や"] = ["(N/N)\\N"]
   lexicon[u"に"] = ["((S\\NP[sbj])/(S\\NP[sbj]))\\N","((S\\NP[sbj])/(S\\NP[sbj]))\\N[adj]","(S[imp]/S[imp])\\N[adj]","(S[null]/S[null])\\N","(S[null]/S[null])\\N[adj]","((S[null]\\NP[obj])/(S[null]\\NP[obj]))\\N","(((S\\NP[sbj])\\NP[obj])/((S\\NP[sbj])\\NP[obj]))\\N[adj]"]
   lexicon[u"へ"] = lexicon[u"に"]
   lexicon[u"で"] = ["((S\\NP[sbj])/(S\\NP[sbj]))\\N","(((S\\NP[sbj])\\NP[obj])/((S\\NP[sbj])\\NP[obj]))\\N","(S[imp]\\S[imp])\\N","(S[null]/S[null])\\N","(S[null]/S[null])\\N[adj]"]
   lexicon[u"と"] = ["((S\\NP[sbj])/(S\\NP[sbj]))\\N","(S/S)\S","(N/N)\\N","(S[null]/(S\\NP[sbj]))\\S","((S\\NP[sbj])/(S\\NP[sbj]))\\S","(S[null]/S[null])\\S"]
   lexicon[u"の"] = ["(N/N[base])\\N","((S[nom]\\NP[sbj])/(S[nom]\\NP[sbj]))\\N"]
   lexicon.setdefault(u"から",[]).extend( ["((S\\NP[sbj])/(S\\NP[sbj]))\\N"] )
   lexicon[u"ようだ"] = ["S\\S"]
   lexicon[u"らしい"] = ["S\\S","(N/N)\\N","(S\\NP[sbj])\\N","(S\\NP[sbj])\\N[adj]","((S\\NP[sbj])\\NP[obj])\\N[adj]"]
   lexicon[u"だろう"] = ["S\\S","(S\\NP[sbj])\\N[adj]","((S\\NP[sbj])\\NP[obj])\\N[adj]"]
   #-- (助詞,接続助詞)
   lexicon[u"ながら"] = ["((S/S)\\NP[sbj])\\IV[cont]","((S/S)\\NP[obj])\\VP[cont]","((S[null]/S[null])\\NP[obj])\\VP[cont]","(S[null]/S[null])\\IV[cont]"]
   lexicon.setdefault(u"つつ",[]).extend( lexicon[u"ながら"] )
   lexicon[u"ので"] = ["(S/S)\\S","(S/S[null])\\S","(S/S)\\S[null]","(S/S[null])\\S[null]"]
   lexicon.setdefault(u"のに",[]).extend( lexicon[u"ので"] )
   lexicon.setdefault(u"から",[]).extend( lexicon[u"ので"] )
   lexicon.setdefault(u"が",[]).extend( lexicon[u"ので"] )
   lexicon.setdefault(u"けど",[]).extend( lexicon[u"ので"] )
   lexicon.setdefault(u"けれど",[]).extend( lexicon[u"ので"] )
   lexicon.setdefault(u"けれども",[]).extend( lexicon[u"ので"] )
   lexicon.setdefault(u"ならば",[]).extend( lexicon[u"ので"] )
   #--
   lexicon.setdefault(u"のだ",[]).extend( ["S[null]\\S[null]","S\\S"] )
   lexicon.setdefault(u"のです",[]).extend( ["S[null]\\S[null]","S\\S"] )
   #-- (助詞,格助詞,連語)
   lexicon[u"について"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"については"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"に於いて"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"に於いては"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"に対して"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"に対しては"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"によって"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"によっては"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"に関して"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"に関しては"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"にあたって"] = ["(S/S)\\N","(S/S)\\S[null]","(S/S)\\S"]
   lexicon[u"によると"] = ["(S/S)\\N","(S[null]/S[null])\\N"]
   lexicon[u"による"] = ["(N/N)\\N"]
   lexicon[u"に於ける"] = ["(N/N)\\N"]
   lexicon[u"にわたる"] = ["(N/N)\\N"]
   lexicon[u"に関する"] = ["(N/N)\\N"]
   #--
   lexicon[u"です"] = ["(S\\NP[sbj])\\N","(S\\NP[sbj])\\N[adj]","((S\\NP[sbj])\\NP[obj])\\N[adj]","S[null]\\N","S[null]\\N[adj]"]
   lexicon[u"ではない"] = lexicon[u"です"]
   lexicon[u"でしょう"] = ["(S\\NP[sbj])\\N","(S\\NP[sbj])\\N[adj]","((S\\NP[sbj])\\NP[obj])\\N[adj]","S[null]\\N","S[null]\\N[adj]"]
   lexicon[u"でした"] = ["(S\\NP[sbj])\\N","(S\\NP[sbj])\\N[adj]","((S\\NP[sbj])\\NP[obj])\\N[adj]","S[null]\\N","S[null]\\N[adj]"]
   lexicon[u"だった"] = lexicon[u"でした"]
   lexicon[u"である"] = lexicon[u"でした"]
   lexicon[u"ます"] = ["(S\\NP[sbj])\\IV[cont]","S[null]\\IV[cont]","((S\\NP[sbj])\\NP[obj])\\VP[cont]","(S[null]\\NP[obj])\\VP[cont]"]
   lexicon[u"ました"] = lexicon[u"ます"]
   lexicon[u"だ"] = ["(S\\NP[sbj])\\N","(S\\NP[sbj])\\N[adj]","((S\\NP[sbj])\\NP[ga-acc])\\N[adj]","((S\\NP[sbj])\\NP[obj])\\N[adj]","S[null]\\N","S[null]\\N[adj]"]
   lexicon[u"ない"] = ["(S\\NP[sbj])\\VP[neg]","((S\\NP[sbj])\\NP[obj])\\IV[neg]","(S\\NP[sbj])\\VP[a-cont]","(N/N)\\VP[a-cont]","((S\\NP[sbj])\\NP[obj])\\TV[neg]","S\\NP[sbj]"]
   lexicon[u"なけれ"] = ["IV[a-hyp]\\IV[neg]","VP[a-hyp]\\TV[neg]"]
   lexicon[u"ません"] = ["(S\\NP[sbj])\\VP[neg]","((S\\NP[sbj])\\NP[obj])\\IV[neg]"]
   lexicon[u"いる"] = ["S\\S[te]","S\\NP[sbj]"]
   lexicon[u"た"] = ["(S\\NP[sbj])\\IV[euph]","((S\\NP[sbj])\\NP[obj])\\VP[euph]","(S[null]\\NP[obj])\\VP[euph]"]
   lexicon[u"ば"] = ["((S/S)\\NP[sbj])\\IV[hyp]","((S/(S\\NP[sbj]))\\NP[sbj])\\IV[hyp]","((S/S)\\NP[sbj])\\IV[a-hyp]","((S/(S\\NP[sbj]))\\NP[sbj])\\IV[a-hyp]"]
   lexicon[u"て"] = ["(S[te]\\NP[sbj])\\IV[cont]","((S/S)\\NP[sbj])\\IV[cont]","(S[te]\\NP[sbj])\\IV[euph]","((S[te]\\NP[sbj])\\NP[obj])\\VP[cont]","((S\\NP[sbj])/(S\\NP[sbj]))\\VP[cont]","((S[null]/S[null])\\NP[obj])\\VP[cont]"]
   #-- 名詞(サ変接続)+"する"
   lexicon.setdefault(u"する",[]).extend( ["(S\\NP[sbj])\\N","S[null]\\N"] )
   lexicon[u"させる"] = lexicon[u"する"]
   lexicon[u"できる"] = lexicon[u"する"]
   tmpl = ["IV[neg]\\N","VP[neg]\\N","IV[cont]\\N","VP[cont]\\N","IV[euph]\\N","VP[euph]\\N"]
   lexicon.setdefault(u"し",[]).extend( tmpl )
   lexicon[u"させ"] = tmpl
   #--
   lexicon[u"圏論"] = ["N"]
   lexicon[u"テレビゲーム"] = ["N"]
   lexicon[u"給付水準"] = ["N"]
   #--
   for line in open( os.path.join(TOPDIR , "sentences.ja.txt") ,encoding='utf-8'):
       line = line.strip()
       if len(line)>0:
           jptest(line , lexicon , type=2)
