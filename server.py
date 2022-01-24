import socket
import pickle
import time
import sys
from _thread import *
import random

questions = [("What Year do Portuguese attack Malacca?\n a) 1952  b) 1511  c) 1841  d) 1832","b"),("In between 8 December 1941 Japanese invented Malaya, Where do first Japanese lay down?\n a) Malacca  b) Penang  c) Kelantan  d) Selangor","b"),("What year do Singapore separated from Malaysia?\n a) 1957  b) 1988  c) 1965  d) 1977","c"),("Year Malaysia independent?\n a) 1988  b) 1880  c) 1957  d) 1999","c"),("When do Malaysia have currency itself?\n a) 1967  b) 1955  c) 1952  d) 1919","a")]
random.shuffle(questions)

boolean = [False, False, False]

whoPressedBuzz = -1

list_of_clients = []

score = [0,0,0]

helper1 = 0
helper2 = 0

class Player():
	def __init__(self, id):
		self.score = 0
		self.id = id
		self.isBuzzerPressed = False
		self.whoPressedBuzzer = id
		self.isPlayerReady = False
		self.isGameReady = False


server = str(sys.argv[1])
port = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.bind((server, port))
except socket.error as e:
	print(e)

s.listen(100)
print("Waiting for a connection, Server Started")

players = [Player(0), Player(1), Player(2)]

def client_thread(conn, curr_player):
	#conn.send("Hey!! Welcome to the Quiz")
	conn.send(pickle.dumps(players[curr_player]))

	MakeAllReady(conn)

	reply = ""

	Quiz(conn, players[curr_player].id)
	conn.close()
	sys.exit()


def MakeAllReady(conn):
	while True:
		try:
			player = pickle.loads(conn.recv(2048))
			if player.isPlayerReady:
				boolean[player.id] = True
				print("Player {} is ready".format(player.id+1))
				conn.send(pickle.dumps(player))
				break
		except:
			pass
	while True:
		try:
			if boolean == [True, True, True]:
				player.isGameReady = True
				print("ALL READY")
				conn.send(pickle.dumps(player))
				break
			conn.send(pickle.dumps(player))
		except:
			pass


def Quiz(conn, player_id):
	global score
	for question in questions:
		if score[0] < 5 and score[1] < 5 and score[2] < 5:
			global whoPressedBuzz
			#player = pickle.loads(conn.recv(2048))
			time.sleep(1)
			print("Sending next question to Player {}, whose answer is option {}.\n".format(player_id+1, question[1]))
			conn.send(str.encode(question[0]+"\n"))
			start_time = time.time()
			conn.send(str.encode("Press Buzzer(Enter key) to give the answer in 20 seconds.\n"))
			helper3 = 0
			while(time.time()-start_time<=20):
				conn.settimeout(0.5)
				#print("{} seconds left".format(time.time()-start_time))
				try:
					data = conn.recv(2048)
					data = data.decode("utf-8")
				except:
					data = None
				if data and whoPressedBuzz == -1:
					whoPressedBuzz = player_id + 1
					conn.send(str.encode("Now, you have 20 seconds to enter the right option among a, b, c and d.\n"))
					helper3 = 1
					break
				if whoPressedBuzz != player_id + 1 and whoPressedBuzz != -1:
					conn.send(str.encode("Player {} has pressed the buzzer. Wait for him/her to answer.\n".format(whoPressedBuzz)))
					helper3 = 1
					break
			answer_time = time.time()
			global helper1
			global helper2
			myhelper = 0
			if helper3==0:
				conn.send(str.encode("Time limit to press the buzzer exceeded.\n The right option is option {}\n".format(question[1])))
			while(time.time()-answer_time<=20 and helper3==1):
				if whoPressedBuzz == player_id + 1:
					conn.settimeout(20)
					try:
						answer = conn.recv(2048)
						answer = answer.decode("utf-8")
						if answer == question[1] + "\n":
							score[player_id] += 1
							whoPressedBuzz = -1
							myhelper = 1
							helper1 = 1
							helper2 = 1
							conn.send(str.encode("Correct answer!! You got 1 point.\n"))
						else:
							score[player_id] -= 0.5
							helper1 = 1
							myhelper = 1
							helper2 = 1
							whoPressedBuzz = -1
							conn.send(str.encode("Ahh!! Wrong answer!! You lose half point.\n"))
					except:
						score[player_id] -= 0.5
						whoPressedBuzz = -1
						helper1 = 1
						helper2 = 1
						conn.send(str.encode("Time limit exceeded. You lose half point.\n"))
				if helper1 == 1:
					helper1 = 0
					whoPressedBuzz = -1
					break
				if helper2 == 1 and helper1 == 0:
					helper2 = 0
					whoPressedBuzz = -1
					break
				if myhelper == 1:
					break
			conn.send(str.encode("Scores:- \n"))
			conn.send(str.encode("         Player 1 : {} points\n".format(score[0])))
			conn.send(str.encode("         Player 2 : {} points\n".format(score[1])))
			conn.send(str.encode("         Player 3 : {} points\n".format(score[2])))
		else:
			break
	
	if score[player_id] >= 5:
		print("Player {} WON\n".format(player_id+1))
		conn.send(str.encode("YOU WON"))
	else:
		if score[0]>=5 and player_id!=0:
			conn.send(str.encode("YOU LOSE. Player {} has won\n".format(1)))
		if score[1]>=5 and player_id!=1:
			conn.send(str.encode("YOU LOSE. Player {} has won\n".format(2)))
		if score[2]>=5 and player_id!=2:
			conn.send(str.encode("YOU LOSE. Player {} has won\n".format(3)))



curr_player = 0
while score[0]<5 and score[1]<5 and score[2]<5:
	s.settimeout(1)
	try:
		conn, addr = s.accept()
		list_of_clients.append(conn)
		print("Connected to:", addr)
	except:
		if score[0]>=5 or score[1]>=5 or score[2]>=5:
			print("Quiz finished")
		continue

	start_new_thread(client_thread, (conn, curr_player))
	curr_player += 1

s.close()