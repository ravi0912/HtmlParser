import re
from bs4 import BeautifulSoup
import urllib
import MySQLdb

# prepare a cursor object using cursor() method
def webpage_spider(link,table):
	db = MySQLdb.connect("localhost","username","password",table )
	cursor = db.cursor()
	sql = "CREATE TABLE IF NOT EXISTS `commentary_table_1` (`m_id` varchar( 10 ) NOT NULL ,`overs` decimal( 4, 2 ) DEFAULT NULL ,`batsman` varchar( 50 ) ,`bowler` varchar( 50 ) ,`runs_scored` int,`how_out` varchar( 50 ) ,`wicketsDown` int)"
	cursor.execute(sql)
	sql = "CREATE TABLE IF NOT EXISTS `india_bat_1`(`m_id` varchar( 10 ) NOT NULL ,`player_name` varchar(50) primary key NOT NULL,`how_out` varchar(50) NOT NULL,`runs_scored` int(11) DEFAULT NULL,`balls_faced` int(11) DEFAULT NULL)"
	cursor.execute(sql)
	sql = "CREATE TRIGGER `scorecard_1` BEFORE INSERT ON `commentary_table_1` FOR EACH ROW begin insert into india_bat_1(m_id, player_name,runs_scored) values (1,new.batsman,new.runs_scored) on duplicate key update runs_scored = runs_scored+ new.runs_scored; end"
	cursor.execute(sql)
	# sql = "CREATE TABLE IF NOT EXISTS `bowling_australia` (`m_id` varchar( 10 ) NOT NULL ,`player_id` varchar(10) primary key NOT NULL,`no_of_balls` decimal(4,2) DEFAULT NULL,`no_of_runs` int(11) DEFAULT NULL,`no_of_wickets` int(11) DEFAULT NULL,`wide` int(11) NOT NULL)"
	# cursor.execute(sql)

	# data = urllib.urlopen('http://www.espncricinfo.com/australia-v-india-2015-16/engine/match/895811.html?innings=1;view=commentary').read()
	data = urllib.urlopen(link).read()
	soup = BeautifulSoup(data)

	a = soup.findAll('div',{'class':'commentary-event'})

	i=0
	wicketsDown = 0
	total_runs_scored = 0
	how_out =''
	runs_scored = 0
	while(i < len(a)):
	# for i in range(0,len(a)):
		# print 'Helo\n',a[i]
		how_out =''
		overs =  a[i].find('div',{'class':'commentary-overs'}).text
		print overs
		text = a[i].find('div',{'class':'commentary-text'}).text
		i=i+1
		text = re.sub('\n', '', text)
		
		a1 = text.split(',')
		bowler = a1[0].split(' to ')[0]
		batsman = a1[0].split(' to ')[1]
		find_runs = re.search('[0-9]+',a1[1])
		if(find_runs):
			runs_scored = find_runs.group(0)
		elif(a1[1] == 'no run'):
			runs_scored = 0
		elif(a1[1] == 'FOUR'):
			runs_scored = 4
		elif(a1[1] == 'SIX'):
			runs_scored = 6
		elif(a1[1] == 'OUT'):
			t1 = a[i].find('div',{'class':'commentary-text'}).text
			find = re.compile(r"^[^0-9]+")
			runs_scored = 0
			how_out = re.sub('&dagger;','',re.search(find,t1).group(0))
			# print "\na\n",how_out
			wicketsDown+= 1
			i=i+1
		sql = "INSERT into commentary_table_1(m_id,overs,batsman,bowler,runs_scored,how_out,wicketsDown) values ('895807','%s','%s','%s','%s','%s','%s')"%(overs, batsman, bowler, runs_scored, how_out, wicketsDown)
		# print sql
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()

	db.close()

webpage_spider('http://www.espncricinfo.com/australia-v-india-2015-16/engine/match/895809.html?innings=1;view=commentary','cricket')