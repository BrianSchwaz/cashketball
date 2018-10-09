import scrapy
from scrapy_splash import SplashRequest
from scrapy.item import Item
from scrapy.item import Field
from .MyItems import Player,PerGame, Totals, PerPos, Advanced, Shooting, Play_By_Play, Playoffs_PerGame, Playoffs_Totals, Playoffs_PerPos, Playoffs_Advanced, Playoffs_Shooting, Playoffs_Play_By_Play, Game, Playoff_Game
import re

player_ids = {}
games_recorded = {}
player_id = 0
total_seasons = 0
total_perPos = 0
total_advanced = 0
total_games = 0
total_games_tr = 0
total_totals = 0
total_playoff_games = 0
total_shooting = 0
total_play_by_play = 0
total_playoffs_per_game = 0
total_playoffs_totals = 0
total_playoffs_per_poss = 0
total_playoffs_advanced = 0
total_playoffs_shooting = 0
total_playoffs_play_by_play = 0

#if none, look for strong font

def hasRing(source):
	if(len(source.xpath('th[@data-stat="season"]/span')) != 0):
		print("This is the output: " + str(source.xpath('th[@data-stat="season"]/span')))
		return "True"
	else:
		return "False"

def getText(source,field):
	if(source.xpath('td[@data-stat="' + field + '"]/text()').extract_first() == None):
		return source.xpath('td[@data-stat="' + field + '"]/strong/text()').extract_first()
	else:
		return source.xpath('td[@data-stat="' + field + '"]/text()').extract_first()

def fillStats(source,item,name,link_fields,fields,this_player_id):
	item["pid"] = this_player_id#player_ids[name]
	item["name"] = name
	if(type(item) is not Game and type(item) is not Playoff_Game):
		item["season"] = source.xpath('th[@data-stat="season"]/a/text()').extract_first()
	else:
		item["ranker"] = source.xpath('th[@data-stat="ranker"]/text()').extract_first()
	for i in range(0,len(link_fields)):
		item[link_fields[i]] = source.xpath('td[@data-stat="' + link_fields[i] + '"]/a/text()').extract_first()
	for i in range(0,len(fields)):
		item[fields[i]] = getText(source,fields[i])
	if(item["team_id"] == None):
		item["team_id"] = source.xpath('th[@data-stat="team_id"]/text()').extract_first()
	return item

def addHyphens(source,item,hyphen_fields):
	for i in range(0,len(hyphen_fields)):
		#print(hyphen_fields[i])
		item[hyphen_fields[i].replace("-","_")] = source.xpath('td[@data-stat="' + hyphen_fields[i].replace("_","-") + '"]/text()').extract_first()
		#print(hyphen_fields[i])
	return item

class PlayerSpider(scrapy.Spider):
	name = "playerSpider"

	start_urls = ["https://www.basketball-reference.com/players/"]#"https://www.basketball-reference.com/players/d/duranke01.html"]
	allowed_domains = ['basketball-reference.com']

	def start_requests(self):
		for url in self.start_urls:
			yield SplashRequest(url=url, callback=self.parse, endpoint='render.html',args={'wait': 5.0})

	def parse_games(self, response):
		global total_games, total_games_tr,total_playoff_games
		#name = response.selector.xpath('//*[@id="footer_header"]/div/span[4]/a/span/text()').extract_first()
		season = response.selector.xpath('//*[@id="all_pgl_basic"]/div[@class="section_heading"]/h2/text()').extract_first()
		games = response.selector.xpath('//table[@id="pgl_basic"]/tbody/tr[@id]')
		games_tr = response.selector.xpath('//table[@id="pgl_basic"]/tbody/tr')
		playoff_games = response.selector.xpath('//table[@id="pgl_basic_playoffs"]/tbody/tr[@id]')
		total_games += len(games)
		total_games_tr += len(games_tr)
		total_playoff_games += len(playoff_games)
		this_player_id = response.meta.get('this_player_id')
		name = response.meta.get('name')

		if(games != None and season != None):
			print(season + ":" + str(len(games)))
		elif(season != None):
			print(season + ":" + "None")
		else:
			print("None Season, Creating new request for:" + response.url)
			yield SplashRequest(url=response.url,callback=self.parse_games,meta={'this_player_id': this_player_id,'name': name},endpoint='render.html',args={'wait': 5.0})
			return
			#print(response.selector.extract())

		print("Total_Games: " + str(total_games))
		print("Total_Games_Tr: " + str(total_games_tr))
		print("Total_Playoff_Games: " + str(total_playoff_games))

		#print("\n\nGames:"+ str(games) + "\n\n")
		link_fields = ["date_game","team_id","opp_id"]
		fields = ["game_season","age","game_location","gs","mp",
			"fg","fga","fg_pct","fg3","fg3a","fg3_pct","ft","fta","ft_pct","orb","drb","trb",
			"ast","stl","blk","tov","pf","pts","game_score","plus_minus"]
		#myYear = response.selector.xpath('//*[@id="meta"]/div[2]/h1/text()').extract_first()
		#print("Length of Games " + str(myYear) + ": " + str(len(games)))
		for game in games:
			stats = Game()
			stats = fillStats(game,stats,name,link_fields,fields,this_player_id)
			game_result = getText(game,"game_result")
			g = getText(game,"game_season")
			#print(game_result)
			if game_result == None or g == None:
				continue
			listResult = list(filter(None,re.split(r'[()\s]\s*',game_result)))
			#split game game_result
			if(len(listResult) == 2):
				winLoss = listResult[0]
				margin = listResult[1]
			elif "-" in listResult[0]:
				winLoss = "L"
				margin = listResult[0]
			elif "+" in listResult[0]:
				winLoss = "W"
				margin = listResult[0]
			else:
				winLoss = listResult[0]
				margin = ""

			stats["game_result"] = margin
			yield stats

		for playoff_game in playoff_games:
			playoff_stats = Playoff_Game()
			stats = fillStats(playoff_game,playoff_stats,name,link_fields,fields,this_player_id)
			game_result = getText(playoff_game,"game_result")
			g = getText(playoff_game,"game_season")
			#print(game_result)
			if game_result == None or g == None:
				continue
			listResult = list(filter(None,re.split(r'[()\s]\s*',game_result)))
			#split game game_result
			if(len(listResult) == 2):
				winLoss = listResult[0]
				margin = listResult[1]
			elif "-" in listResult[0]:
				winLoss = "L"
				margin = listResult[0]
			elif "+" in listResult[0]:
				winLoss = "W"
				margin = listResult[0]
			else:
				winLoss = listResult[0]
				margin = ""

			playoff_stats["game_result"] = margin
			yield playoff_stats


	def parse_player(self,response):
		global player_id,total_seasons,total_perPos,total_advanced,total_totals,total_shooting,total_play_by_play,total_playoffs_per_game,total_playoffs_totals,total_playoffs_per_poss,total_playoffs_advanced,total_playoffs_shooting,total_playoffs_play_by_play

		name = response.selector.xpath('//h1[@itemprop="name"]/text()').extract_first()
		per_game = response.selector.xpath('//table[@id="per_game"]/tbody/tr')#[@class="full_table"]')
		totals = response.selector.xpath('//table[@id="totals"]/tbody/tr')#[@class="full_table"]')
		per_pos = response.selector.xpath('//table[@id="per_poss"]/tbody/tr')#[@class="full_table"]')
		advanced = response.selector.xpath('//table[@id="advanced"]/tbody/tr')#[@class="full_table"]')
		shooting = response.selector.xpath('//table[@id="shooting"]/tbody/tr')#[@class="full_table"]')
		play_by_play = response.selector.xpath('//table[@id="advanced_pbp"]/tbody/tr')#[@class="full_table"]')
		playoffs = response.selector.xpath('//table[@id="playoffs_per_game"]/tbody/tr')#[@class="full_table"]')
		playoffs_totals = response.selector.xpath('//table[@id="playoffs_totals"]/tbody/tr')#[@class="full_table"]')
		playoffs_per_poss = response.selector.xpath('//table[@id="playoffs_per_poss"]/tbody/tr')#[@class="full_table"]')
		playoffs_advanced = response.selector.xpath('//table[@id="playoffs_advanced"]/tbody/tr')#[@class="full_table"]')
		playoffs_shooting = response.selector.xpath('//table[@id="playoffs_shooting"]/tbody/tr')#[@class="full_table"]')
		playoffs_play_by_play = response.selector.xpath('//table[@id="playoffs_advanced_pbp"]/tbody/tr')#[@class="full_table"]')

		if(name != None):
			player_id += 1
			this_player_id = player_id
			player_ids[name] = player_id
			total_seasons += len(per_game)
			total_perPos += len(per_pos)
			total_advanced += len(advanced)
			total_totals += len(totals)
			total_shooting += len(shooting)
			total_play_by_play += len(play_by_play)
			total_playoffs_per_game += len(playoffs)
			total_playoffs_totals += len(playoffs_totals)
			total_playoffs_per_poss += len(playoffs_per_poss)
			total_playoffs_advanced += len(playoffs_advanced)
			total_playoffs_shooting += len(playoffs_shooting)
			total_playoffs_play_by_play += len(playoffs_play_by_play)
			stats = Player()
			stats["name"] = name
			stats["pid"] = this_player_id
			stats["weight"] = response.selector.xpath('//*[@id="meta"]/div/p[4]/span[1]/text()').extract_first()
			stats["height"] = response.selector.xpath('//*[@id="meta"]/div/p[4]/span[2]/text()').extract_first()
			yield stats

		else:
			print("None Player, Creating new request for:" + response.url)
			yield SplashRequest(url=response.url,callback=self.parse_player,endpoint='render.html',args={'wait': 5.0})
			return

		for per in per_game:
			stats = PerGame()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp_per_g","fg_per_g","fga_per_g","fg_pct","fg3_per_g",
				"fg3a_per_g","fg3_pct","fg2_per_g","fg2a_per_g","fg2_pct","efg_pct","ft_per_g",
				"fta_per_g","ft_pct","orb_per_g","drb_per_g","trb_per_g","ast_per_g","stl_per_g",
				"blk_per_g","tov_per_g","pf_per_g","pts_per_g"]

			game_link = per.xpath('th[@data-stat="season"]/a/@href').extract_first()
			link = response.urljoin(game_link)
			yield SplashRequest(url=link,callback=self.parse_games,meta={'this_player_id': this_player_id,'name': name},endpoint='render.html',args={'wait': 5.0})
			if(game_link != None):
				yield fillStats(per,stats,name,link_fields,fields,this_player_id)
			#break

		for total in totals:
			stats = Totals()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp","fg","fga","fg_pct","fg3","fg3a","fg3_pct","fg2",
				"fg2a","fg2_pct","efg_pct","ft","fta","ft_pct","orb","drb","trb","ast","stl","blk",
				"tov","pf","pts"]
			yield fillStats(total,stats,name,link_fields,fields,this_player_id)
			#break

		
		for pos in per_pos:
			stats = PerPos()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp","fg_per_poss","fga_per_poss","fg_pct","fg3_per_poss",
				"fg3a_per_poss","fg3_pct","fg2_per_poss","fg2a_per_poss","fg2_pct","ft_per_poss",
				"fta_per_poss","ft_pct","orb_per_poss","drb_per_poss","trb_per_poss","ast_per_poss",
				"stl_per_poss","blk_per_poss","tov_per_poss","pf_per_poss","pts_per_poss","off_rtg",
				"def_rtg"]
			yield fillStats(pos,stats,name,link_fields,fields,this_player_id)

		for adv in advanced:
			stats = Advanced()
			link_fields = ["team_id","lg_id"]
			#hyphen_fields = ["ws-dum","bpm-dum"]
			fields = ["age","pos","g","mp","per","ts_pct","fg3a_per_fga_pct","fta_per_fga_pct",
				"orb_pct","drb_pct","trb_pct","ast_pct","stl_pct","blk_pct","tov_pct","usg_pct",
				"ows","dws","ws","ws_per_48","obpm","dbpm","bpm","vorp"]
			stats = fillStats(adv,stats,name,link_fields,fields,this_player_id)
			yield stats #addHyphens(adv,stats,hyphen_fields)

		for shoot in shooting:
			stats = Shooting()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","mp","fg_pct","avg_dist","fg2a_pct_fga","pct_fga_00_03",
				"pct_fga_03_10","pct_fga_10_16","pct_fga_16_xx","fg3a_pct_fga","fg2_pct",
				"fg_pct_00_03","fg_pct_03_10","fg_pct_10_16","fg_pct_16_xx","fg3_pct","fg2_pct_ast",
				"pct_fg2_dunk","fg2_dunk","fg3_pct_ast","pct_fg3a_corner","fg3_pct_corner",
				"fg3a_heave","fg3_heave"]
			yield fillStats(shoot,stats,name,link_fields,fields,this_player_id)

		for play in play_by_play:
			stats = Play_By_Play()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","mp","pct_1","pct_2","pct_3","pct_4","pct_5","plus_minus_on",
				"plus_minus_net","tov_bad_pass","tov_lost_ball","tov_other","fouls_shooting",
				"fouls_blocking","fouls_offensive","fouls_take","astd_pts","drawn_shooting",
				"and1s","fga_blkd"]
			yield fillStats(play,stats,name,link_fields,fields,this_player_id)

		for playoff in playoffs:
			stats = Playoffs_PerGame()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp_per_g","fg_per_g","fga_per_g","fg_pct","fg3_per_g",
				"fg3a_per_g","fg3_pct","fg2_per_g","fg2a_per_g","fg2_pct","efg_pct","ft_per_g",
				"fta_per_g","ft_pct","orb_per_g","drb_per_g","trb_per_g","ast_per_g","stl_per_g",
				"blk_per_g","tov_per_g","pf_per_g","pts_per_g"]
			stats["ring"] = hasRing(playoff)
			yield fillStats(playoff,stats,name,link_fields,fields,this_player_id)

		for playoff_total in playoffs_totals:
			stats = Playoffs_Totals()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp","fg","fga","fg_pct","fg3","fg3a","fg3_pct","fg2",
				"fg2a","fg2_pct","efg_pct","ft","fta","ft_pct","orb","drb","trb","ast","stl","blk",
				"tov","pf","pts"]
			stats["ring"] = hasRing(playoff_total)
			yield fillStats(playoff_total,stats,name,link_fields,fields,this_player_id)

		for playoff_pos in playoffs_per_poss:
			stats = Playoffs_PerPos()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp","fg_per_poss","fga_per_poss","fg_pct","fg3_per_poss",
				"fg3a_per_poss","fg3_pct","fg2_per_poss","fg2a_per_poss","fg2_pct","ft_per_poss",
				"fta_per_poss","ft_pct","orb_per_poss","drb_per_poss","trb_per_poss","ast_per_poss",
				"stl_per_poss","blk_per_poss","tov_per_poss","pf_per_poss","pts_per_poss","off_rtg",
				"def_rtg"]
			stats["ring"] = hasRing(playoff_pos)
			yield fillStats(playoff_pos,stats,name,link_fields,fields,this_player_id)

		for playoff_adv in playoffs_advanced:
			stats = Playoffs_Advanced()
			link_fields = ["team_id","lg_id"]
			#hyphen_fields = ["ws_dum","bpm_dum"]
			fields = ["age","pos","g","mp","per","ts_pct","fg3a_per_fga_pct","fta_per_fga_pct",
				"orb_pct","drb_pct","trb_pct","ast_pct","stl_pct","blk_pct","tov_pct","usg_pct",
				"ows","dws","ws","ws_per_48","obpm","dbpm","bpm","vorp"]
			stats = fillStats(playoff_adv,stats,name,link_fields,fields,this_player_id)
			stats["ring"] = hasRing(playoff_adv)
			yield stats #addHyphens(playoff_adv,stats,hyphen_fields)

		for playoff_shoot in playoffs_shooting:
			stats = Playoffs_Shooting()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","mp","fg_pct","avg_dist","fg2a_pct_fga","pct_fga_00_03",
				"pct_fga_03_10","pct_fga_10_16","pct_fga_16_xx","fg3a_pct_fga","fg2_pct",
				"fg_pct_00_03","fg_pct_03_10","fg_pct_10_16","fg_pct_16_xx","fg3_pct","fg2_pct_ast",
				"pct_fg2_dunk","fg2_dunk","fg3_pct_ast","pct_fg3a_corner","fg3_pct_corner",
				"fg3a_heave","fg3_heave"]
			stats["ring"] = hasRing(playoff_shoot)
			yield fillStats(playoff_shoot,stats,name,link_fields,fields,this_player_id)

		for playoff_play in playoffs_play_by_play:
			stats = Playoffs_Play_By_Play()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","mp","pct_1","pct_2","pct_3","pct_4","pct_5","plus_minus_on",
				"plus_minus_net","tov_bad_pass","tov_lost_ball","tov_other","fouls_shooting",
				"fouls_blocking","fouls_offensive","fouls_take","astd_pts","drawn_shooting",
				"and1s","fga_blkd"]
			stats["ring"] = hasRing(playoff_play)
			yield fillStats(playoff_play,stats,name,link_fields,fields,this_player_id)

		print("Total_Seasons: " + str(total_seasons))
		print("Total_perPos: " + str(total_perPos))
		print("Total_advanced: " + str(total_advanced))
		print("Total_totals: " + str(total_totals))
		print("Total_shooting: " + str(total_shooting))
		print("Total_play_by_play: " + str(total_play_by_play))
		print("Total_playoffs_per_game: " + str(total_playoffs_per_game))
		print("Total_playoffs_totals: " + str(total_playoffs_totals))
		print("Total_playoffs_per_poss: " + str(total_playoffs_per_poss))
		print("Total_playoffs_advanced: " + str(total_playoffs_advanced))
		print("Total_playoffs_shooting: " + str(total_playoffs_shooting))
		print("Total_playoffs_play_by_play: " + str(total_playoffs_play_by_play))

	def parse_list(self, response):
		#players = response.selector.xpath('//table[@id="players"]/tbody/tr')
		players = response.selector.xpath('//table[@id="players"]/tbody')
		player_links = response.selector.xpath('//table[@id="players"]/tbody/tr/th/a')
		present_player_links = response.selector.xpath('//table[@id="players"]/tbody/tr/th/strong/a')

		for i in range(0,len(player_links)):#for player_link in player_links:
			link = response.urljoin(player_links[i].xpath('@href').extract_first())
			yield SplashRequest(url=link,callback=self.parse_player,endpoint='render.html',args={'wait': 5.0})
		for i in range(0,len(present_player_links)):#for present_player_link in present_player_links:
			link = response.urljoin(present_player_links[i].xpath('@href').extract_first())
			yield SplashRequest(url=link,callback=self.parse_player,endpoint='render.html',args={'wait': 5.0})

		
	def parse(self,response):
		alphabet = response.selector.xpath('//div[@id="content"]/div[@id="all_alphabet"]/div/ul/li')
		print(len(alphabet))
		for letter in alphabet:
			letter_link = letter.xpath('a/@href').extract_first()
			if(letter_link != None):
				link = response.urljoin(letter_link)
				yield SplashRequest(url=link,callback=self.parse_list,endpoint='render.html',args={'wait':5.0})
		

		'''
		name = response.selector.xpath('//h1[@itemprop="name"]/text()').extract_first()
		per_game = response.selector.xpath('//table[@id="per_game"]/tbody/tr[@class="full_table"]')
		totals = response.selector.xpath('//table[@id="totals"]/tbody/tr[@class="full_table"]')
		per_pos = response.selector.xpath('//table[@id="per_poss"]/tbody/tr[@class="full_table"]')
		advanced = response.selector.xpath('//table[@id="advanced"]/tbody/tr[@class="full_table"]')
		shooting = response.selector.xpath('//table[@id="shooting"]/tbody/tr[@class="full_table"]')
		play_by_play = response.selector.xpath('//table[@id="advanced_pbp"]/tbody/tr[@class="full_table"]')
		playoffs = response.selector.xpath('//table[@id="playoffs_per_game"]/tbody/tr[@class="full_table"]')
		playoffs_totals = response.selector.xpath('//table[@id="playoffs_totals"]/tbody/tr[@class="full_table"]')
		playoffs_per_poss = response.selector.xpath('//table[@id="playoffs_per_poss"]/tbody/tr[@class="full_table"]')
		playoffs_advanced = response.selector.xpath('//table[@id="playoffs_advanced"]/tbody/tr[@class="full_table"]')
		playoffs_shooting = response.selector.xpath('//table[@id="playoffs_shooting"]/tbody/tr[@class="full_table"]')
		playoffs_play_by_play = response.selector.xpath('//table[@id="playoffs_advanced_pbp"]/tbody/tr[@class="full_table"]')

		for i in range(7,len(per_game)):
			stats = PerGame()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp_per_g","fg_per_g","fga_per_g","fg_pct","fg3_per_g",
				"fg3a_per_g","fg3_pct","fg2_per_g","fg2a_per_g","fg2_pct","efg_pct","ft_per_g",
				"fta_per_g","ft_pct","orb_per_g","drb_per_g","trb_per_g","ast_per_g","stl_per_g",
				"blk_per_g","tov_per_g","pf_per_g","pts_per_g"]
			
			game_link = per_game[i].xpath('th[@data-stat="season"]/a/@href').extract_first()
			link = response.urljoin(game_link)
			yield scrapy.Request(url=link,callback=self.parse_games)
			yield fillStats(per_game[i],stats,name,link_fields,fields,this_player_id)

		
		for total in totals:
			stats = Totals()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp","fg","fga","fg_pct","fg3","fg3a","fg3_pct","fg2",
				"fg2a","fg2_pct","efg_pct","ft","fta","ft_pct","orb","drb","trb","ast","stl","blk",
				"tov","pf","pts"]
			yield fillStats(total,stats,name,link_fields,fields,this_player_id)

		for pos in per_pos:
			stats = PerPos()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp","fg_per_poss","fga_per_poss","fg_pct","fg3_per_poss",
				"fg3a_per_poss","fg3_pct","fg2_per_poss","fg2a_per_poss","fg2_pct","ft_per_poss",
				"fta_per_poss","ft_pct","orb_per_poss","drb_per_poss","trb_per_poss","ast_per_poss",
				"stl_per_poss","blk_per_poss","tov_per_poss","pf_per_poss","pts_per_poss","off_rtg",
				"def_rtg"]
			yield fillStats(pos,stats,name,link_fields,fields,this_player_id)

		for adv in advanced:
			stats = Advanced()
			link_fields = ["team_id","lg_id"]
			hyphen_fields = ["ws-dum","bpm-dum"]
			fields = ["age","pos","g","mp","per","ts_pct","fg3a_per_fga_pct","fta_per_fga_pct",
				"orb_pct","drb_pct","trb_pct","ast_pct","stl_pct","blk_pct","tov_pct","usg_pct",
				"ows","dws","ws","ws_per_48","obpm","dbpm","bpm","vorp"]
			stats = fillStats(adv,stats,name,link_fields,fields,this_player_id)
			yield addHyphens(adv,stats,hyphen_fields)

		for shoot in shooting:
			stats = Shooting()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","mp","fg_pct","avg_dist","fg2a_pct_fga","pct_fga_00_03",
				"pct_fga_03_10","pct_fga_10_16","pct_fga_16_xx","fg3a_pct_fga","fg2_pct",
				"fg_pct_00_03","fg_pct_03_10","fg_pct_10_16","fg_pct_16_xx","fg3_pct","fg2_pct_ast",
				"pct_fg2_dunk","fg2_dunk","fg3_pct_ast","pct_fg3a_corner","fg3_pct_corner",
				"fg3a_heave","fg3_heave"]
			yield fillStats(shoot,stats,name,link_fields,fields,this_player_id)

		for play in play_by_play:
			stats = Play_By_Play()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","mp","pct_1","pct_2","pct_3","pct_4","pct_5","plus_minus_on",
				"plus_minus_net","tov_bad_pass","tov_lost_ball","tov_other","fouls_shooting",
				"fouls_blocking","fouls_offensive","fouls_take","astd_pts","drawn_shooting",
				"and1s","fga_blkd"]
			yield fillStats(play,stats,name,link_fields,fields,this_player_id)

		for playoff in playoffs:
			stats = Playoffs_PerGame()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp_per_g","fg_per_g","fga_per_g","fg_pct","fg3_per_g",
				"fg3a_per_g","fg3_pct","fg2_per_g","fg2a_per_g","fg2_pct","efg_pct","ft_per_g",
				"fta_per_g","ft_pct","orb_per_g","drb_per_g","trb_per_g","ast_per_g","stl_per_g",
				"blk_per_g","tov_per_g","pf_per_g","pts_per_g"]
			yield fillStats(playoff,stats,name,link_fields,fields,this_player_id)

		for playoff_total in playoffs_totals:
			stats = Playoffs_Totals()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp","fg","fga","fg_pct","fg3","fg3a","fg3_pct","fg2",
				"fg2a","fg2_pct","efg_pct","ft","fta","ft_pct","orb","drb","trb","ast","stl","blk",
				"tov","pf","pts"]
			yield fillStats(playoff_total,stats,name,link_fields,fields,this_player_id)

		for playoff_pos in playoffs_per_poss:
			stats = Playoffs_PerPos()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","gs","mp","fg_per_poss","fga_per_poss","fg_pct","fg3_per_poss",
				"fg3a_per_poss","fg3_pct","fg2_per_poss","fg2a_per_poss","fg2_pct","ft_per_poss",
				"fta_per_poss","ft_pct","orb_per_poss","drb_per_poss","trb_per_poss","ast_per_poss",
				"stl_per_poss","blk_per_poss","tov_per_poss","pf_per_poss","pts_per_poss","off_rtg",
				"def_rtg"]
			yield fillStats(playoff_pos,stats,name,link_fields,fields,this_player_id)

		for playoff_adv in playoffs_advanced:
			stats = Playoffs_Advanced()
			link_fields = ["team_id","lg_id"]
			hyphen_fields = ["ws_dum","bpm_dum"]
			fields = ["age","pos","g","mp","per","ts_pct","fg3a_per_fga_pct","fta_per_fga_pct",
				"orb_pct","drb_pct","trb_pct","ast_pct","stl_pct","blk_pct","tov_pct","usg_pct",
				"ows","dws","ws","ws_per_48","obpm","dbpm","bpm","vorp"]
			stats = fillStats(playoff_adv,stats,name,link_fields,fields,this_player_id)
			yield addHyphens(playoff_adv,stats,hyphen_fields)

		for playoff_shoot in playoffs_shooting:
			stats = Playoffs_Shooting()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","mp","fg_pct","avg_dist","fg2a_pct_fga","pct_fga_00_03",
				"pct_fga_03_10","pct_fga_10_16","pct_fga_16_xx","fg3a_pct_fga","fg2_pct",
				"fg_pct_00_03","fg_pct_03_10","fg_pct_10_16","fg_pct_16_xx","fg3_pct","fg2_pct_ast",
				"pct_fg2_dunk","fg2_dunk","fg3_pct_ast","pct_fg3a_corner","fg3_pct_corner",
				"fg3a_heave","fg3_heave"]
			yield fillStats(playoff_shoot,stats,name,link_fields,fields,this_player_id)

		for playoff_play in playoffs_play_by_play:
			stats = Playoffs_Play_By_Play()
			link_fields = ["team_id","lg_id"]
			fields = ["age","pos","g","mp","pct_1","pct_2","pct_3","pct_4","pct_5","plus_minus_on",
				"plus_minus_net","tov_bad_pass","tov_lost_ball","tov_other","fouls_shooting",
				"fouls_blocking","fouls_offensive","fouls_take","astd_pts","drawn_shooting",
				"and1s","fga_blkd"]
			yield fillStats(playoff_play,stats,name,link_fields,fields,this_player_id)
		'''







