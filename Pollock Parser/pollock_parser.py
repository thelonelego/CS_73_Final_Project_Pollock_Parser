"""
pollock_parser.py
Matt Rossi & J. Patrick Lewis
COSC 73 Final Project
Professor Reddy
November 18, 2014
"""

from cs1lib import clear, draw_circle, start_graphics, enable_smoothing
from cs1lib import *
import random
import argparse
import sys
import ImageFilter

#####TEXT ANALYSIS##########################################################
#this class analyzes the text and provides a number of useful information about it
#that we will later use to draw the corresponding Pollock-ized image
class Analyzed_Text:
	def __init__(self, file):
		self.file = file

	#get a unigram dictionary on the text
	def get_unigram_dictionary(self):
		unigram_dictionary = {}
		punctuation = ['.',',',';',':','\'','?','#','$','%','*','(',')','@','!','-','--','*','&','^','`','~','"','\'']
		in_file = open(self.file, 'r')
		#Total word count
		self.count = 0
		for line in in_file:
			#split each line into strings of each word in the line.  
			#E.g. "the man walks" becomes "the" "man" "walks."
			line = line.split()

			for word in line:
				#increase count by 1
				self.count += 1

				#make all words in line lowercase
				word = word.lower()

				#remove all unwanted punctuation
				for letter in word:
					if letter in punctuation:
						word = word.replace(letter, '')
				
				#if word is in the unigram dictionary then add 1
				#to the value of that word in the unigram dictionary		
				if word in unigram_dictionary:
					unigram_dictionary[word] += 1
				else:
					unigram_dictionary[word] = 1
		
		in_file.close()
		return unigram_dictionary

	#returns the nubmer of positive words and the number of negative words
	def pos_or_neg(self, unigram_dictionary):
		#corpora of positive/negative words (from the provided resources on Piazza)
		positive_words_file = open('positive_words.txt')
		negative_words_file = open('negative_words.txt')
		positive_count = 0
		negative_count = 0

		#increment the positive count
		for word in positive_words_file:
			#strip whitespace from the word
			word = word.strip()
			if word in unigram_dictionary:
				positive_count += unigram_dictionary[word]
		positive_words_file.close()

		#do the same with the negative words
		for word in negative_words_file:
			word = word.strip()
			if word in unigram_dictionary:
				negative_count += unigram_dictionary[word]
		negative_words_file.close()

		return (positive_count, negative_count)

	#returns dictionaries of words->colors & words->emotions
	def get_emot_color_dicts(self):
		color_file = open('words_colors.txt')
		emotion_file = open('words_emotions.txt')

		colors = {}
		emotions = {}

		for line in color_file:
			line = line.split()
			colors[line[0]] = []
			for color in line[1:]:
				colors[line[0]].append(color)

		for line in emotion_file:
			line = line.split()
			emotions[line[0]] = []
			for emotion in line[1:]:
				emotions[line[0]].append(emotion)

		color_file.close()
		emotion_file.close()

		return (colors, emotions)

#helper method to generate text files with words with associated emotions/colors 
#NOTE: we only used this method once to make text files with only relevant words
#(i.e. those that either mapped to colors or to emotions)
def make_text_files():
	common_words_file = open('most_common.txt', 'r')
	emotion_file = open('words_emotions.txt', 'w')
	color_file = open('words_colors.txt', 'w')
	emotions = ['anticipation', 'joy', 'surprise', 'trust', 'anger', 'sadness', 'love', 'disgust', 'fear']
	colors = ['black', 'brown', 'white', 'beige', 'grey', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink']
	
	# for the emotions
	for line in common_words_file:
		emotional = 0
		line = line.split()
		if len(line) != 0:
			for word in line[1:]:
				if word in emotions:
					emotional += 1
		if emotional > 0:
			emotion_file.write(line[0] + ' ')
		if len(line) != 0:
			for word in line[1:]:
				if word in emotions:
					emotion_file.write(word + ' ')
		if emotional != 0:
			emotion_file.write('\n')

	common_words_file.close()
	common_words_file = open('most_common.txt')

	# for the colors
	for line in common_words_file:
		color_count = 0
		line = line.split()
		if len(line) != 0:
			for word in line[1:]:
				if word in colors:
					color_count += 1
		if color_count > 0:
			color_file.write(line[0] + ' ')
		if len(line) != 0:
			for word in line[1:]:
				if word in colors:
					color_file.write(word + ' ')
		if color_count != 0:
			color_file.write('\n')

	emotion_file.close()
	color_file.close()

#reads a text file and makes a dictionary of colors and their mappings (one for each emotion)
#(i.e. black maps to (1, 1, 1))
def colors_to_rgb():
	#if it's some very obvious ones, like sadness or anger (use blue and red color schemes respectively)
	#otherwise, randomize
	#see text_emotion for notes on prevailing_emotion
	if prevailing_emotion == 'anger':
		file = 'anger_colors.txt'
	elif prevailing_emotion == 'fear':
		file = 'fear_colors.txt'
	elif prevailing_emotion == 'sadness':
		file = 'sadness_colors.txt'
	elif prevailing_emotion == 'disgust':
		file = 'disgust_colors.txt'
	elif prevailing_emotion == 'love':
		file = 'love_colors.txt'
	elif prevailing_emotion == 'joy':
		file = 'joy_colors.txt'
	elif prevailing_emotion == 'surprise':
		file = 'surprise_colors.txt'
	#we don't have a good visual representation for 'anticipation' as an emotion, so use trust, which is pretty general
	else:
		file = 'trust_colors.txt'

	#now we make the files that map colors to RGB values
	positive_color_file = open(file)
	negative_color_file = open(file)
	pos_color_rgb_dict = {}
	neg_color_rgb_dict = {}
	
	# for the positive colors
	for line in positive_color_file:
		line = line.split()
		pos_color_rgb_dict[line[0]] = [float(line[1])/250, float(line[2])/250, float(line[3])/250]

	# for the negative colors
	for line in negative_color_file:
		line = line.split()
		neg_color_rgb_dict[line[0]] = [float(line[1])/250, float(line[2])/250, float(line[3])/250]

	positive_color_file.close()
	negative_color_file.close()

	return (pos_color_rgb_dict, neg_color_rgb_dict)						

#go through the text and determine what emotion it most closely corresponds to
def text_emotion():
	text_emotion_count = {'anticipation': 0, 'anger': 0, 'disgust': 0, 'fear': 0, 'love': 0, 'trust': 0, 'sadness': 0, 'surprise': 0, 'joy': 0}
	for word in unigram_dictionary:
		if word in emotion_dictionary:
			for i in range(unigram_dictionary[word]):
				for emotion in emotion_dictionary[word]:
					text_emotion_count[emotion] += 1
	
	count = 0
	top_emotion = ' '

	#if the emotion is 'anticipation', we get a count of the second most frequent emotion,
	#since it doesn't have a very telling color palette
	for element in text_emotion_count:
		if text_emotion_count[element] > count:
			if element != 'anticipation':
				count = text_emotion_count[element]
				top_emotion = element

	return top_emotion

#####DRAWING################################################################
#the following function actually draws the image
def draw_polluck():

	enable_smoothing()
	enable_fill()
	disable_stroke()

	#finds the average color given a list of colors (does this for each word)
	def color_averager(color_list):
		r_total = 0
		g_total = 0
		b_total = 0
		num_colors = 0

		#if the text is positive, replace black, brown, and grey
		#NOTE: the following code that is commented out was removed after we decided to incorporate a different
		#color palette for each emotion
		if is_positive:
			rgbs = positive_rgb
			# for i in range(len(color_list)):
			# 	if color_list[i] == 'black':
			# 		color_list[i] = 'purple'
			# 	if color_list[i] == 'brown':
			# 		color_list[i] = 'beige'
			# 	if color_list[i] == 'grey':
			# 		color_list[i] = 'yellow'
		#if the text is negative, replace pink and yellow
		else:
			rgbs = negative_rgb
			# for i in range(len(color_list)):
			# 	if color_list[i] == 'pink':
			# 		color_list[i] = 'purple'
			# 	if color_list[i] == 'yellow':
			# 		color_list[i] = 'orange'
			# 	if color_list[i] == 'white':
			# 		color_list[i] = 'orange'

		# go through each color in the color list, look up its rgb value, and average them
		for color in color_list:
			r_total += rgbs[color][0]
			g_total += rgbs[color][1]
			b_total += rgbs[color][2]
			num_colors += 1

		# now that we have the total color, take the averages
		average_r = r_total / num_colors
		average_g = g_total / num_colors
		average_b = b_total / num_colors

		average_color = (average_r, average_g, average_b)
		return average_color

	# for each emotion, we have a list of associated colors (from the Saif Mohammad paper)
	# helper method to give us a color from an emotion
	def emotion_to_colors(emotion):
		emotion_color_dict = {}
		emotion_color_dict['anticipation'] = ['white','green','red']
		emotion_color_dict['anger'] = ['black','red','orange']
		emotion_color_dict['disgust'] = ['black','brown','green']
		emotion_color_dict['fear'] = ['black','red','grey']
		emotion_color_dict['love'] = ['red','pink','purple']
		emotion_color_dict['trust'] = ['white','blue','yellow']
		emotion_color_dict['sadness'] = ['grey','blue', 'black']
		emotion_color_dict['surprise'] = ['red','yellow','white']
		emotion_color_dict['joy'] = ['yellow','white','purple']

		if emotion == 'anticipation':
			color = random.choice(emotion_color_dict['anticipation'])
		if emotion == 'anger':
			color = random.choice(emotion_color_dict['anger'])
		if emotion == 'disgust':
			color = random.choice(emotion_color_dict['disgust'])
		if emotion == 'fear':
			color = random.choice(emotion_color_dict['fear'])
		if emotion == 'love':
			color = random.choice(emotion_color_dict['love'])
		if emotion == 'trust':
			color = random.choice(emotion_color_dict['trust'])
		if emotion == 'sadness':
			color = random.choice(emotion_color_dict['sadness'])
		if emotion == 'surprise':
			color = random.choice(emotion_color_dict['surprise'])
		if emotion == 'joy':
			color = random.choice(emotion_color_dict['joy'])

		# #same as color averager
		# if is_positive:
		# 	if color == 'black':
		# 		color = 'purple'
		# 	if color == 'brown':
		# 		color = 'beige'
		# 	if color == 'grey':
		# 		color = 'yellow'
		# else:
		# 	if color == 'white':
		# 		color = 'orange'
		# 	if color == 'pink':
		# 		color = 'purple'
		# 	if color == 'yellow':
		# 		color = 'orange'

		return color

	#returns a number between 0 and 3 (inclusive) 
	#used to determine which shape to draw for each word
	def random_number():
		number = random.randint(0, 3)
		return number

	#returns the font size of a word to be drawn based on the number of emotions that are associated with it
	def font_size(word):
		num_emotions = 0
		if word in emotion_dictionary:
			for emotion in emotion_dictionary[word]:
				num_emotions += 1
		return 10 + num_emotions * len(word)

	#if the text is positive overall
	#this process is identical for texts that are negative, so refer to this section of code for notes
	if is_positive:
		#set the clear color equal to the corresponding white color in the palette
		set_clear_color(positive_rgb['white'][0],positive_rgb['white'][1],positive_rgb['white'][2])
		clear()
		drawn_words = 0

		#we want to get a good density of words
		while drawn_words < 2000:
			#draw the words
			for word in unigram_dictionary:
				#draws according to the color of the word
				if word in color_dictionary:
					drawn_words += 1
					#does this however many times the word is seen
					for i in range(unigram_dictionary[word]):
						average_color = color_averager(color_dictionary[word])				
						#draws average color
						rand_x = random.randint(0, WINDOWWIDTH)
						rand_y = random.randint(0, WINDOWHEIGHT)
						set_fill_color(average_color[0], average_color[1], average_color[2])
						set_stroke_color(average_color[0], average_color[1], average_color[2])
						#draw shapes if we're drawing shapes
						if draw_shapes:
							shape_num = random_number()
							if shape_num == 0:
								draw_ellipse(rand_x, rand_y, random.randint(len(word), len(word)*2), random.randint(len(word), len(word)*2))
							if shape_num == 1:
								second_corner_x = random.randint(rand_x-20, rand_x+20)
								second_corner_y = random.randint(rand_y-20, rand_y+20)
								third_corner_x = random.randint(rand_x-20, rand_x+20)
								third_corner_y = random.randint(rand_y-20, rand_y+20)
								draw_triangle(rand_x, rand_y, second_corner_x, second_corner_y, third_corner_x, third_corner_y)
							if shape_num == 2:
								width = random.randint(10, 20)
								height = random.randint(10, 20)
								draw_rectangle(rand_x, rand_y, width, height)
							if shape_num == 3:
								second_corner_x = random.randint(rand_x-30, rand_x+30)
								second_corner_y = random.randint(rand_y-30, rand_y+30)
								enable_stroke()
								set_stroke_width(random.randint(3,10))
								draw_line(rand_x, rand_y, second_corner_x, second_corner_y)
								disable_stroke()
						#if we're not drawing shapes, draw the words
						else:
							enable_stroke()
							set_font_size(font_size(word))
							draw_text(word, rand_x, rand_y)
							disable_stroke()
						
						#draws each color
						for i in range(len(color_dictionary[word])):
							rand_x = random.randint(0, WINDOWWIDTH)
							rand_y = random.randint(0, WINDOWHEIGHT)
							set_fill_color(positive_rgb[color_dictionary[word][i]][0], positive_rgb[color_dictionary[word][i]][1], positive_rgb[color_dictionary[word][i]][2])
							set_stroke_color(positive_rgb[color_dictionary[word][i]][0], positive_rgb[color_dictionary[word][i]][1], positive_rgb[color_dictionary[word][i]][2])
							if draw_shapes:	
								shape_num = random_number()
								if shape_num == 0:
									draw_ellipse(rand_x, rand_y, random.randint(len(word), len(word)*2), random.randint(len(word), len(word)*2))
								if shape_num == 1:
									second_corner_x = random.randint(rand_x-20, rand_x+20)
									second_corner_y = random.randint(rand_y-20, rand_y+20)
									third_corner_x = random.randint(rand_x-20, rand_x+20)
									third_corner_y = random.randint(rand_y-20, rand_y+20)
									draw_triangle(rand_x, rand_y, second_corner_x, second_corner_y, third_corner_x, third_corner_y)
								if shape_num == 2:
									width = random.randint(10, 20)
									height = random.randint(10, 20)
									draw_rectangle(rand_x, rand_y, width, height)
								if shape_num == 3:
									second_corner_x = random.randint(rand_x-30, rand_x+30)
									second_corner_y = random.randint(rand_y-30, rand_y+30)
									enable_stroke()
									set_stroke_width(random.randint(3,10))
									draw_line(rand_x, rand_y, second_corner_x, second_corner_y)
									disable_stroke()
							else:
								enable_stroke()
								set_font_size(font_size(word))
								draw_text(word, rand_x, rand_y)
								disable_stroke()
				#draws accoridng to emotion of the word
				#for each emotion that the word corresponds to, prints out a random color associated with each
				if word in emotion_dictionary:
					drawn_words += 1
					for i in range(unigram_dictionary[word]):
						for i in range(3):
							for emotion in emotion_dictionary[word]:
								rand_x = random.randint(0, WINDOWWIDTH)
								rand_y = random.randint(0, WINDOWHEIGHT)
								emotion_color = emotion_to_colors(emotion)
								set_fill_color(positive_rgb[emotion_color][0], positive_rgb[emotion_color][1], positive_rgb[emotion_color][2])
								set_stroke_color(positive_rgb[emotion_color][0], positive_rgb[emotion_color][1], positive_rgb[emotion_color][2])
								if draw_shapes:
									shape_num = random_number()
									if shape_num == 0:
										draw_ellipse(rand_x, rand_y, random.randint(len(word), len(word)*2), random.randint(len(word), len(word)*2))
									if shape_num == 1:
										second_corner_x = random.randint(rand_x-20, rand_x+20)
										second_corner_y = random.randint(rand_y-20, rand_y+20)
										third_corner_x = random.randint(rand_x-20, rand_x+20)
										third_corner_y = random.randint(rand_y-20, rand_y+20)
										draw_triangle(rand_x, rand_y, second_corner_x, second_corner_y, third_corner_x, third_corner_y)
									if shape_num == 2:
										width = random.randint(10, 20)
										height = random.randint(10, 20)
										draw_rectangle(rand_x, rand_y, width, height)
									if shape_num == 3:
										second_corner_x = random.randint(rand_x-30, rand_x+30)
										second_corner_y = random.randint(rand_y-30, rand_y+30)
										enable_stroke()
										set_stroke_width(random.randint(3,10))
										draw_line(rand_x, rand_y, second_corner_x, second_corner_y)
										disable_stroke()
								else:
									enable_stroke()
									set_font_size(font_size(word))
									draw_text(word, rand_x, rand_y)
									disable_stroke()

	#if negative
	else:
		set_clear_color(negative_rgb['black'][0],negative_rgb['black'][1],negative_rgb['black'][2])
		clear()
		drawn_words = 0

		while drawn_words < 2000:
			#draw the words
			for word in unigram_dictionary:
				#draws according to the color of the word
				if word in color_dictionary:
					drawn_words += 1
					#does this however many times the word is seen
					for i in range(unigram_dictionary[word]):
						average_color = color_averager(color_dictionary[word])
						
						#draws average color
						rand_x = random.randint(0, WINDOWWIDTH)
						rand_y = random.randint(0, WINDOWHEIGHT)
						set_fill_color(average_color[0], average_color[1], average_color[2])
						set_stroke_color(average_color[0], average_color[1], average_color[2])
						if draw_shapes:
							shape_num = random_number()
							if shape_num == 0:
								draw_ellipse(rand_x, rand_y, random.randint(len(word), len(word)*2), random.randint(len(word), len(word)*2))
							if shape_num == 1:
								second_corner_x = random.randint(rand_x-20, rand_x+20)
								second_corner_y = random.randint(rand_y-20, rand_y+20)
								third_corner_x = random.randint(rand_x-20, rand_x+20)
								third_corner_y = random.randint(rand_y-20, rand_y+20)
								draw_triangle(rand_x, rand_y, second_corner_x, second_corner_y, third_corner_x, third_corner_y)
							if shape_num == 2:
								width = random.randint(10, 20)
								height = random.randint(10, 20)
								draw_rectangle(rand_x, rand_y, width, height)
							if shape_num == 3:
								second_corner_x = random.randint(rand_x-30, rand_x+30)
								second_corner_y = random.randint(rand_y-30, rand_y+30)
								enable_stroke()
								set_stroke_width(5)
								draw_line(rand_x, rand_y, second_corner_x, second_corner_y)
								disable_stroke()
						else:
							enable_stroke()
							set_font_size(font_size(word))
							draw_text(word, rand_x, rand_y)
							disable_stroke()

						
						#draws each color
						for i in range(len(color_dictionary[word])):
							rand_x = random.randint(0, WINDOWWIDTH)
							rand_y = random.randint(0, WINDOWHEIGHT)
							set_fill_color(negative_rgb[color_dictionary[word][i]][0], negative_rgb[color_dictionary[word][i]][1], negative_rgb[color_dictionary[word][i]][2])
							set_stroke_color(negative_rgb[color_dictionary[word][i]][0], negative_rgb[color_dictionary[word][i]][1], negative_rgb[color_dictionary[word][i]][2])
							if draw_shapes:
								shape_num = random_number()
								if shape_num == 0:
									draw_ellipse(rand_x, rand_y, random.randint(len(word), len(word)*2), random.randint(len(word), len(word)*2))
								if shape_num == 1:
									second_corner_x = random.randint(rand_x-20, rand_x+20)
									second_corner_y = random.randint(rand_y-20, rand_y+20)
									third_corner_x = random.randint(rand_x-20, rand_x+20)
									third_corner_y = random.randint(rand_y-20, rand_y+20)
									draw_triangle(rand_x, rand_y, second_corner_x, second_corner_y, third_corner_x, third_corner_y)
								if shape_num == 2:
									width = random.randint(10, 20)
									height = random.randint(10, 20)
									draw_rectangle(rand_x, rand_y, width, height)
								if shape_num == 3:
									second_corner_x = random.randint(rand_x-30, rand_x+30)
									second_corner_y = random.randint(rand_y-30, rand_y+30)
									enable_stroke()
									set_stroke_width(5)
									draw_line(rand_x, rand_y, second_corner_x, second_corner_y)
									disable_stroke()
							else:
								enable_stroke()
								set_font_size(font_size(word))
								draw_text(word, rand_x, rand_y)
								disable_stroke()
				#draws accoridng to emotion of the word
				#for each emotion that the word corresponds to, prints out a random color associated with each
				if word in emotion_dictionary:
					drawn_words += 1
					for i in range(unigram_dictionary[word]):
						for i in range(3):
							for emotion in emotion_dictionary[word]:
								rand_x = random.randint(0, WINDOWWIDTH)
								rand_y = random.randint(0, WINDOWHEIGHT)
								emotion_color = emotion_to_colors(emotion)
								set_fill_color(negative_rgb[emotion_color][0], negative_rgb[emotion_color][1], negative_rgb[emotion_color][2])
								set_stroke_color(negative_rgb[emotion_color][0], negative_rgb[emotion_color][1], negative_rgb[emotion_color][2])
								if draw_shapes:
									shape_num = random_number()
									if shape_num == 0:
										draw_ellipse(rand_x, rand_y, random.randint(len(word), len(word)*2), random.randint(len(word), len(word)*2))
									if shape_num == 1:
										second_corner_x = random.randint(rand_x-20, rand_x+20)
										second_corner_y = random.randint(rand_y-20, rand_y+20)
										third_corner_x = random.randint(rand_x-20, rand_x+20)
										third_corner_y = random.randint(rand_y-20, rand_y+20)
										draw_triangle(rand_x, rand_y, second_corner_x, second_corner_y, third_corner_x, third_corner_y)
									if shape_num == 2:
										width = random.randint(10, 20)
										height = random.randint(10, 20)
										draw_rectangle(rand_x, rand_y, width, height)
									if shape_num == 3:
										second_corner_x = random.randint(rand_x-30, rand_x+30)
										second_corner_y = random.randint(rand_y-30, rand_y+30)
										enable_stroke()
										set_stroke_width(5)
										draw_line(rand_x, rand_y, second_corner_x, second_corner_y)
										disable_stroke()
								else:
									enable_stroke()
									set_font_size(font_size(word))
									draw_text(word, rand_x, rand_y)
									disable_stroke()
if __name__ == '__main__':
	###RUN THE PROGRAM###
    #we need these to be accessible anywhere in the program
    global unigram_dictionary, color_dictionary, emotion_dictionary, prevailing_emotion, positive_rgb, negative_rgb, is_positive, draw_shapes, WINDOWWIDTH, WINDOWHEIGHT
    
    #get input from the user
    parser = argparse.ArgumentParser()
    parser.add_argument('-file', type=str, help='text to draw', required = True) #what is our body of text?
    parser.add_argument('-type', type=str, help='words or shapes', required = True) #how do we want to represent it
    args = parser.parse_args()
    
    #do we draw words or shapes?
    if args.type == 'words':
    	draw_shapes = False
    else:
    	draw_shapes = True
    file_to_draw = args.file

    sonnet = Analyzed_Text(file_to_draw)
    
    #unigram dictionary
    unigram_dictionary = sonnet.get_unigram_dictionary()
    
    #set the window width and height relative to the length of the text
    WINDOWWIDTH = int(600)
    WINDOWHEIGHT = int(600)
    
    #positive and negative word count
    (pos_ct, neg_ct) = sonnet.pos_or_neg(unigram_dictionary)
    
    #used to set the color scheme
    is_positive = False
    if pos_ct > neg_ct:
    	is_positive = True
    
    # dicitonaries that map words to colors and words to emotions
    (color_dictionary, emotion_dictionary) = sonnet.get_emot_color_dicts()
    prevailing_emotion = text_emotion()
    
    # ditionaries that map colors to their rgb values
    (positive_rgb, negative_rgb) = colors_to_rgb()

    start_graphics(draw_polluck, 'Pollock Paints: ' + file_to_draw + '!', WINDOWWIDTH, WINDOWHEIGHT, True)