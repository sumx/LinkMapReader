#!/usr/bin/python
#coding:utf-8

import os,sys
from string import Template

class SymbolReader(object):

	def __init__(self, linkmapdir):
		super(SymbolReader, self).__init__()
		self.linkmapdir=linkmapdir

	#read objs From linkmapdir
	def readObjectFrom(self):
		f=open(self.linkmapdir, "r")
		shouldSkip=True
		dic={}
		for line in f:
			if line.find("Object files:")!=-1 and shouldSkip:
				shouldSkip=False
				continue
			else:
				if line.find("# Sections:")!=-1:
					break
				else:
					objInfo=line.split(']')
					if len(objInfo)==2:
						index=objInfo[0]+']'
						name=objInfo[1]
						dic[index.strip()]=name.strip()
		f.close
		return dic
				
	#read linkmapdir 
	def readSymbolsInfoFrom(self):
		f=open(self.linkmapdir, "r")
		shouldSkip=0
		dic={}
		for line in f:
			if line.find("# Address	Size    	File  Name")!=-1 and  shouldSkip==0:
				shouldSkip=1
				continue
			else:
				if shouldSkip==1:
					symbolInfo=line.split("	")
					if len(symbolInfo)==3:
						offset=symbolInfo[0].strip()
						symbolSize=symbolInfo[1].strip()
						leftStr=symbolInfo[2]
						indexAndSymbolName=leftStr.split('] ')
						index=indexAndSymbolName[0]+"]".strip()
						symbolName=indexAndSymbolName[1].strip()
						if index in dic:
							dic[index].append({"Address":offset,"size":symbolSize,"index":index,"name":symbolName})
						else:
							dic[index]=[];
							dic[index].append({"Address":offset,"size":symbolSize,"index":index,"name":symbolName})
		f.close
		return dic		

	def generateHtmlWithSymbolInfo(self,info,objname):
		objNameList=objname.split(os.sep)
		totalSize=self.generateSymbolSize(info)
		html="<h3 id="+objNameList[len(objNameList)-1]+">"+objNameList[len(objNameList)-1]+":   all symbol size "+str(totalSize)+"</h3>"
		html = html+"<table class=\"table table-bordered\"><tr><td>名称</td><td>Size(byte)</td></tr>"
		ta = Template('<tr><td width="90%">$name</td><td width="10%">$size</td></tr>')
		info=sorted(info,key = lambda x:x['size'], reverse=True)
		for sinfo in info:
			html=html+ta.safe_substitute({"name":sinfo["name"],"size":int(sinfo["size"],16)})
		html=html+"</table>"	
		return html

	def generateSymbolSize(self,item):
		sum=0
		for sinfo in item:
			sum=sum+int(sinfo["size"],16)
		return sum

	def generateSymbolLink(self,key):
		objNameList=key.split(os.sep)
		return "<li><a href=\"#"+objNameList[len(objNameList)-1]+"\">"+objNameList[len(objNameList)-1]+"</a></li>" 	

	def generateHtmlFormatDetail(self):
		objs=self.readObjectFrom()
		symbols=self.readSymbolsInfoFrom()
		tsum=0
		html="<!DOCTYPE html><html lang=\"zh-CN\"><meta charset=\"utf-8\"><link href=\"http://cdn.bootcss.com/bootstrap/3.3.5/css/bootstrap.min.css\" rel=\"stylesheet\"><link href=\"http://v3.bootcss.com/assets/css/docs.min.css\" rel=\"stylesheet\"><style>.table{word-break: break-all;}</style><script src=\"http://cdn.bootcss.com/jquery/3.0.0-alpha1/jquery.min.js\"></script><script src=\"http://cdn.bootcss.com/bootstrap/3.3.5/js/bootstrap.min.js\"></script><body><div class=\"container bs-docs-container\"><div class=\"row\"><div class=\"col-md-9 table-responsive\">"
		navHtml=""
		for key in sorted(symbols.keys()):
			item=symbols[key]	
			tsum=tsum+self.generateSymbolSize(item)
			html=html+self.generateHtmlWithSymbolInfo(item,objs[key])
			navHtml=navHtml+self.generateSymbolLink(objs[key])
		html=html+"</div><div class=\"col-md-3\"><nav class=\"bs-docs-sidebar hidden-print hidden-xs hidden-sm\" data-spy=\"affix\"><ul class=\"nav bs-docs-sidenav\">"+navHtml+"</ul></nav></div><footer class=\"bs-docs-footer\" role=\"contentinfo\"></footer></body></html>"
		outFile=open(os.getcwd()+"/result.html",'w')
		outFile.write(html)
		print "all linked size:"+str(tsum)

	def generateObjSizeDetail(self):
		objs=self.readObjectFrom()
		symbols=self.readSymbolsInfoFrom()
		tsum=0
		for key in sorted(symbols.keys()):
			item=symbols[key]	
			tsum=tsum+self.generateSymbolSize(item)
			sum=0
			for sinfo in item:
				sum=sum+int(sinfo["size"],16)
			objNameSplited=objs[key].split(os.sep)	
			print objNameSplited[len(objNameSplited)-1]+" "+str(sum)
		print "all linked size:"+str(tsum)


if __name__=='__main__':
	dir = sys.argv[1]
	argLen=len(sys.argv)
	mode = (argLen==3 and sys.argv[2]) or ""
	if os.path.isfile(dir) == True:
		reader=SymbolReader(dir)
		if mode.strip() == "html":
			reader.generateHtmlFormatDetail()
		else:
			reader.generateObjSizeDetail()
	else:
		print "should config linkmap path"
		sys.exit(0)


 
