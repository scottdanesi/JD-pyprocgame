import procgame
import locale
import time
from procgame import *
import os.path
import random

curr_file_path = os.path.dirname(os.path.abspath( __file__ ))
sound_path = curr_file_path + "/sound/FX/"
voice_path = curr_file_path + "/sound/Voice/"
music_path = curr_file_path + "/sound/"

class ModeCompletedHurryup(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(ModeCompletedHurryup, self).__init__(game, priority)
		self.countdown_layer = dmd.TextLayer(128/2, 7, self.game.fonts['jazz18'], "center")
		self.banner_layer = dmd.TextLayer(128/2, 7, self.game.fonts['jazz18'], "center")
		self.layer = dmd.GroupedLayer(128, 32, [self.countdown_layer, self.banner_layer])
		full_voice_path = voice_path + 'hurryup/'
		filename = 'wow thats awesome.wav'
		self.game.sound.register_sound('collected', full_voice_path+filename)
		filename = 'great shot.wav'
		self.game.sound.register_sound('collected', full_voice_path+filename)
		filename = 'incredible shot.wav'
		self.game.sound.register_sound('collected', full_voice_path+filename)
		filename = 'jd - excellent.wav'
		self.game.sound.register_sound('collected', full_voice_path+filename)
	
	def mode_started(self):
		self.banner_layer.set_text("HURRY-UP!", 3)
		#Placeholder for "Shoot the Subway Audio"
		self.seconds_remaining = 13
		self.update_and_delay()
		self.update_lamps()
		self.game.coils.tripDropTarget.pulse(40)
		self.delay(name='trip_check', event_type=None, delay=.400, handler=self.trip_check)
		self.already_collected = False

	def trip_check(self):
		if self.game.switches.dropTargetD.is_inactive():
			self.game.coils.tripDropTarget.pulse(40)
			self.delay(name='trip_check', event_type=None, delay=.400, handler=self.trip_check)

	def sw_dropTargetD_inactive_for_400ms(self, sw):
		self.game.coils.tripDropTarget.pulse(40)
		self.delay(name='trip_check', event_type=None, delay=.400, handler=self.trip_check)

	def update_lamps(self):
		self.game.lamps.pickAPrize.schedule(schedule=0x33333333, cycle_seconds=0, now=True)

	def mode_stopped(self):
		#self.drop_target_mode.animated_reset(1.0)
		self.game.lamps.pickAPrize.disable()
		self.cancel_delayed(['grace', 'countdown', 'trip_check'])
		#if self.game.switches.popperL.is_open():
		#	self.game.coils.popperL.pulse(40)
		self
	
	def sw_subwayEnter1_closed(self, sw):
		self.collected()
		self.game.sound.play_voice('collected')
		self.cancel_delayed(['grace', 'countdown', 'trip_check'])
		self.already_collected = True
		self.banner_layer.set_text('Well Done!')
		self.layer = dmd.GroupedLayer(128, 32, [self.banner_layer])
	
	# Ball might jump over first switch.  Use 2nd switch as a catchall.
	def sw_subwayEnter2_closed(self, sw):
		if not self.already_collected:
			self.banner_layer.set_text('Well Done!')
			self.layer = dmd.GroupedLayer(128, 32, [self.banner_layer])
			self.collected()
			self.cancel_delayed(['grace', 'countdown', 'trip_check'])
	
	def update_and_delay(self):
		self.countdown_layer.set_text("%d seconds" % (self.seconds_remaining))
		self.delay(name='countdown', event_type=None, delay=1, handler=self.one_less_second)
		
	def one_less_second(self):
		self.seconds_remaining -= 1
		if self.seconds_remaining >= 0:
			self.update_and_delay()
		else:
			self.delay(name='grace', event_type=None, delay=2, handler=self.delayed_removal)
			
	def delayed_removal(self):
		self.expired()

class ModeTimer(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(ModeTimer, self).__init__(game, priority)
		self.timer = 0;

	def mode_stopped(self):
		self.stop()

	def start(self, time):
		# Tell the mode how much time it gets, if it cares.
		self.timer_update(time)
		self.timer = time
		self.delay(name='decrement timer', event_type=None, delay=1, handler=self.decrement_timer)

	def stop(self):
		self.timer = 0
		self.cancel_delayed('decrement timer')

	def add(self,adder):
		self.timer += adder 

	def pause(self, pause_unpause=True):
		if pause_unpause:
			self.cancel_delayed('decrement timer')
		elif self.timer > 0:
			self.delay(name='decrement timer', event_type=None, delay=1, handler=self.decrement_timer)

	def decrement_timer(self):
		if self.timer > 0:
			self.timer -= 1
			self.delay(name='decrement timer', event_type=None, delay=1, handler=self.decrement_timer)
			self.timer_update(self.timer)
		else:
			print "% 10.3f Timer calling callback" % (time.time())
			self.failed()
			self.callback()

	def failed(self):
		pass

	def timer_update(self, time):
		pass

class PlayIntro(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(PlayIntro, self).__init__(game, priority)
		self.frame_counter = 0

	def mode_started(self):
		self.frame_counter = 0
		self.next_frame()
		self.update_gi(False, 'all')
		# Disable the flippers
		self.game.enable_flippers(enable=False)

	def mode_stopped(self):
		self.cancel_delayed('intro')
		self.update_gi(True, 'all')
		# Enable the flippers
		self.game.enable_flippers(enable=True)

	def setup(self, mode, exit_function, exit_function_param, instruction_layers):
		self.exit_function = exit_function
		self.exit_function_param = exit_function_param
		self.mode = mode
		self.instruction_layers = instruction_layers
		self.layer = dmd.GroupedLayer(128, 32, self.instruction_layers[0])

	def update_gi(self, on, num):
		for i in range(1,5):
			if num == 'all' or num == i:
				if on:
					self.game.lamps['gi0' + str(i)].pulse(0)
				else:
					self.game.lamps['gi0' + str(i)].disable()

	def sw_flipperLwL_active(self, sw):
		if self.game.switches.flipperLwR.is_active():
			self.cancel_delayed('intro')
			self.exit_function(self.exit_function_param)	

	def sw_flipperLwR_active(self, sw):
		if self.game.switches.flipperLwL.is_active():
			self.cancel_delayed('intro')
			self.exit_function(self.exit_function_param)	

	def next_frame(self):
		if self.frame_counter != len(self.instruction_layers):
			self.delay(name='intro', event_type=None, delay=2, handler=self.next_frame)
			self.layer = dmd.GroupedLayer(128, 32, self.instruction_layers[self.frame_counter])
			self.frame_counter += 1
		else:
			self.exit_function(self.exit_function_param)	


class ChainFeature(modes.Scoring_Mode, ModeTimer):
	"""docstring for AttractMode"""
	def __init__(self, game, priority, name):
		super(ChainFeature, self).__init__(game, priority)
		self.completed = False
		self.name = name
		self.countdown_layer = dmd.TextLayer(127, 1, self.game.fonts['tiny7'], "right")
		self.name_layer = dmd.TextLayer(1, 1, self.game.fonts['tiny7'], "left").set_text(name)
		self.score_layer = dmd.TextLayer(128/2, 10, self.game.fonts['num_14x10'], "center")
		self.status_layer = dmd.TextLayer(128/2, 26, self.game.fonts['tiny7'], "center")
		self.layer = dmd.GroupedLayer(128, 32, [self.countdown_layer, self.name_layer, self.score_layer, self.status_layer])
		

	def register_callback_function(self, function):
		self.callback = function

	def play_music(self):
		self.game.sound.stop_music()
		self.game.sound.play_music('mode', loops=-1)

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(name)
		instruction_layers = [[layer1]]
		return instruction_layers

	def mode_tick(self):
		score = self.game.current_player().score
		if score == 0:
			self.score_layer.set_text('00')
		else:
			self.score_layer.set_text(locale.format("%d",score,True))

	def timer_update(self, timer):
		self.countdown_layer.set_text(str(timer))

class Pursuit(ChainFeature):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(Pursuit, self).__init__(game, priority, 'Pursuit')
		difficulty = self.game.user_settings['Gameplay']['Chain feature difficulty']
		if difficulty == 'easy':
			self.shots_required_for_completion = 3
		elif difficulty == 'medium':
			self.shots_required_for_completion = 4
		else:
			self.shots_required_for_completion = 5

		full_voice_path = voice_path + 'pursuit/'
		filename = 'bank robbery suspects fleeing.wav'
		self.game.sound.register_sound('pursuit intro', full_voice_path+filename)
		filename = 'great shot.wav'
		self.game.sound.register_sound('good shot', full_voice_path+filename)
		filename = 'incredible shot.wav'
		self.game.sound.register_sound('good shot', full_voice_path+filename)
		filename = 'jd - excellent.wav'
		self.game.sound.register_sound('good shot', full_voice_path+filename)
		filename = 'jd - in pursuit 1.wav'
		self.game.sound.register_sound('in pursuit', full_voice_path+filename)
		filename = 'jd - in pursuit 2.wav'
		self.game.sound.register_sound('in pursuit', full_voice_path+filename)
		filename = 'suspects apprehended.wav'
		self.game.sound.register_sound('complete', full_voice_path+filename)
		filename = 'suspects got away.wav'
		self.game.sound.register_sound('failed', full_voice_path+filename)

	def mode_started(self):
		self.shots = 0
		self.update_status()
		self.update_lamps()
		time = self.game.sound.play_voice('pursuit intro')
		self.delay(name='response', event_type=None, delay=time+0.5, handler=self.response)

	def response(self):
		self.game.sound.play_voice('in pursuit')

	def update_lamps(self):
		self.game.coils.flasherPursuitL.schedule(schedule=0x00030003, cycle_seconds=0, now=True)
		self.game.coils.flasherPursuitR.schedule(schedule=0x03000300, cycle_seconds=0, now=True)

	def update_status(self):
		status = 'Shots made: ' + str(self.shots) + '/' + str(self.shots_required_for_completion)
		self.status_layer.set_text(status)
		

	def mode_stopped(self):
		self.game.coils.flasherPursuitL.disable()
		self.game.coils.flasherPursuitR.disable()

	# Award shot if ball diverted for multiball.  Ensure it was a fast
	# shot rather than one that just trickles in.
	def sw_leftRampToLock_active(self, sw):
		if self.game.switches.leftRampEnter.time_since_change() < 0.5:
			self.shots += 1
			self.game.score(10000)
			self.check_for_completion()

	def sw_leftRampExit_active(self, sw):
		self.shots += 1
		self.game.score(10000)
		self.check_for_completion()

	def sw_rightRampExit_active(self, sw):
		self.shots += 1
		self.game.score(10000)
		self.check_for_completion()

	def check_for_completion(self):
		self.update_status()
		if self.shots == self.shots_required_for_completion:
			self.game.sound.play_voice('complete')
			self.completed = True
			self.game.score(50000)
			print "% 10.3f Pursuit calling callback" % (time.time())
			self.callback()
		else:
			self.game.sound.play_voice('good shot')

	def failed(self):
		self.game.sound.play_voice('failed')
			

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		font_small = self.game.fonts['tiny7']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer21 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer22 = dmd.TextLayer(128/2, 24, font_small, "center").set_text("Shoot " + str(self.shots_required_for_completion) + " L/R ramp shots")
		instruction_layers = [[layer1], [layer21, layer22]]
		return instruction_layers
	
class Blackout(ChainFeature):
#########################################################
#Blackout v1.0
#This is a mode where Dredd tries to locate an illegal
#rave that is causing blackouts in Mega City One.  Once
#he gets entry to the rave he must capture as many of
#the party-goers as he can.
#########################################################
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(Blackout, self).__init__(game, priority, 'Blackout')
		difficulty = self.game.user_settings['Gameplay']['Chain feature difficulty']
		###############MODE CONSTANTS AND REGISTRATIONS###############################################################
		###Shots Required For Completion of Mode######################################################################
		if difficulty == 'easy':
			self.shots_required_for_completion = 1
		elif difficulty == 'medium':
			self.shots_required_for_completion = 1
		else:
			self.shots_required_for_completion = 2
			
		###Ball Save time (in seconds)################################################################################
		self.rave_ball_save_time = 10
		###Ball Save Number of Balls to Save##########################################################################
		self.rave_ball_save_number_of_saves = 1
		###Initial Time to Shoot The Center Ramp (in seconds)#########################################################
		self.rave_initial_timer = 30
		###Lightshow Delay Time After Rave Started (in seconds)#######################################################
		self.rave_lightshow_delay = .1 #This is used to match the lights with the start of the rave music############
		###Timer Increment After Raver Captured (in seconds)##########################################################
		self.rave_timer_inc = 7
		###Raver Captured Score Award#################################################################################
		self.rave_capture_score = 30000
		###Mode Completion Score Award################################################################################
		self.rave_completion_score = 50000
		###Register Rave Lampshows####################################################################################
		self.game.lampctrl.register_show('rave_lamps', curr_file_path + "/lamps/flashers_blackout_rave.lampshow")
		self.game.lampctrl.register_show('blackout_right_ramp', curr_file_path + "/lamps/blackout_seq_perp5.lampshow")
		self.game.lampctrl.register_show('blackout_sniper_tower', curr_file_path + "/lamps/blackout_seq_perp3.lampshow")
		self.game.lampctrl.register_show('blackout_subway', curr_file_path + "/lamps/blackout_seq_subway.lampshow")
		###Register Audio#############################################################################################
		self.game.sound.register_sound('capture_raver', voice_path + "crimescenes/great shot.wav")
		self.game.sound.register_sound('capture_raver', voice_path + "crimescenes/incredible shot.wav")
		self.game.sound.register_sound('shoot_rt_ramp', voice_path + "crimescenes/great shot.wav")
		###Register music for Blackout Mode
		#self.game.sound.register_music('rave', music_path + "blackout_rave_music1.mp3")
		self.game.sound.register_music('rave', music_path + "Scott Danesi - TBD2.wav")
		self.game.sound.register_music('blackout_music', music_path + "blackout_rave_music1.mp3")
		###############END MODE CONSTANTS AND REGISTRATIONS###########################################################
			
	def mode_started(self):
		#self.shots will be used as ravers captured
		self.shots = 0
		self.rave_started = 0
		self.jackpot_shot_num = 0
		self.subway_missed_switch = 1
		self.lightshow_started = 0
		self.update_status()
		filename = curr_file_path + "/dmd/blackout.dmd"
		if os.path.isfile(filename):
			anim = dmd.Animation().load(filename)
			self.game.base_game_mode.jd_modes.play_animation(anim, 'high', repeat=False, hold=False, frame_time=3)
		self.update_lamps()
		#self.game.sound.stop_music()
		#self.game.sound.play_music('rave', loops=-1)

	def update_status(self):
		if self.rave_started == 1:
			#Rave Started
			status = 'Ravers Captured: ' + str(self.shots)
			self.status_layer.set_text(status)
		else:
			#Rave not started
			status = 'Shoot the Center Ramp '
			self.status_layer.set_text(status)
			
			
	def blackout_start_rave_seq(self):
		self.rave_started = 1
		self.jackpot_shot_num = 1
		self.trip_check()
		self.update_status()
		#Switch Music Track
		self.game.sound.stop_music()
		self.game.sound.play_music('rave', loops=-1)
		#check if ball save is active and add 10 seconds or give a 10 second ball save
		if self.game.ball_save.timer > 0:
			#self.game.set_status('+10 second ball saver')
			self.game.ball_save.add(self.rave_ball_save_time)
		else:
			self.game.ball_save.callback = None
			#self.game.set_status('save  ' + str(self.game.trough.num_balls_in_play) + ' balls')
			#self.game.ball_save.start(num_balls_to_save=self.game.trough.num_balls_in_play, time=10, now=True, allow_multiple_saves=True)
			self.game.ball_save.start(num_balls_to_save=self.rave_ball_save_number_of_saves, time=self.rave_ball_save_time, now=True, allow_multiple_saves=True)
			
		#put time on the clock to match the music
		self.timer = self.rave_initial_timer
		#delay the flashers and lamps to match music
		self.delay(name='rave_start_delay', event_type=None, delay=self.rave_lightshow_delay, handler=self.rave_start_delay)
		
	def increment_rave_jackpot(self):
		#increment Jackpot Shot Number
		if self.jackpot_shot_num == 3:
			#Cycle Back to 1
			self.jackpot_shot_num = 1
		else:
			#increment Jackpot
			self.jackpot_shot_num += 1
			
	def rave_start_delay(self):
		self.lightshow_started = 1
		self.update_lamps()

	def mode_stopped(self):
		self.disable_lamps()
		self.game.lamps.gi01.pulse(0)
		self.game.lamps.gi02.pulse(0)
		self.game.lamps.gi03.pulse(0)
		self.game.lamps.gi04.pulse(0)

	def update_lamps(self):
		#disable lamps
		self.disable_lamps()
		#Enable Blackout Ramp Lamp and Arrow
		self.game.lamps.blackoutJackpot.schedule(schedule=0x000F000F, cycle_seconds=0, now=True)
		self.game.lamps.tankCenter.schedule(schedule=0xF000F000, cycle_seconds=0, now=True)
		#Check if Blackout Rave started
		if self.rave_started == 1:
			#Rave Started
			#Update GI
			self.game.lamps.gi01.disable()
			self.game.lamps.gi02.disable()
			self.game.lamps.gi03.disable()
			self.game.lamps.gi04.disable()
			#Start Rave Jackpot Lampshows
			#self.game.coils.flashersLowerLeft.schedule(schedule=0x00000003, cycle_seconds=0, now=True)
			#self.game.coils.flasherPursuitL.schedule(schedule=0x00000030, cycle_seconds=0, now=True)
			self.game.coils.flasherCursedEarth.schedule(schedule=0x00000003, cycle_seconds=0, now=True)
			self.game.coils.flasherGlobe.schedule(schedule=0x00000030, cycle_seconds=0, now=True)
			self.game.coils.flashersRtRamp.schedule(schedule=0x00000300, cycle_seconds=0, now=True)
			#self.game.coils.flasherPursuitR.schedule(schedule=0x00300000, cycle_seconds=0, now=True)
			self.game.coils.flasherBlackout.schedule(schedule=0x03030303, cycle_seconds=0, now=True)
			#self.disable_jackpot_lights()
			if self.jackpot_shot_num == 1:
				#Shoot the Subway
				self.game.lamps.dropTargetJ.schedule(schedule=0x000F000F, cycle_seconds=0, now=True)
				self.game.lamps.dropTargetE.schedule(schedule=0x000F000F, cycle_seconds=0, now=True)
				self.game.lamps.dropTargetU.schedule(schedule=0x00F000F0, cycle_seconds=0, now=True)
				self.game.lamps.dropTargetG.schedule(schedule=0x00F000F0, cycle_seconds=0, now=True)
				self.game.lamps.dropTargetD.schedule(schedule=0x0F000F00, cycle_seconds=0, now=True)
				self.game.lamps.multiballJackpot.schedule(schedule=0xFFFFFFFF, cycle_seconds=0, now=True)
				self.game.lamps.pickAPrize.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
				self.game.coils.flasherGlobe.schedule(schedule=0x33330030, cycle_seconds=0, now=True)
				#self.game.lampctrl.play_show('blackout_subway', repeat=True)
			elif self.jackpot_shot_num == 2:
				#Shoot right Ramp 
				self.game.lamps.perp5W.schedule(schedule=0xC000C000, cycle_seconds=0, now=True)
				self.game.lamps.perp5R.schedule(schedule=0x0C000C00, cycle_seconds=0, now=True)
				self.game.lamps.perp5Y.schedule(schedule=0x00C000C0, cycle_seconds=0, now=True)
				self.game.lamps.perp5G.schedule(schedule=0x000C000C, cycle_seconds=0, now=True)
				self.game.coils.flasherPursuitR.schedule(schedule=0x33330000, cycle_seconds=0, now=True)
				#self.game.lampctrl.play_show('blackout_right_ramp', repeat=True)
			elif self.jackpot_shot_num == 3:
				#Shoot Sniper Tower
				self.game.lamps.perp3W.schedule(schedule=0xF000F000, cycle_seconds=0, now=True)
				self.game.lamps.perp3R.schedule(schedule=0x0F000F00, cycle_seconds=0, now=True)
				self.game.lamps.perp3Y.schedule(schedule=0x00F000F0, cycle_seconds=0, now=True)
				self.game.lamps.perp3G.schedule(schedule=0x000F000F, cycle_seconds=0, now=True)
				self.game.coils.flashersRtRamp.schedule(schedule=0x33330000, cycle_seconds=0, now=True)
				#self.game.lampctrl.play_show('blackout_sniper_tower', repeat=True)
		else:
			#Rave not started
			#Update GI
			self.game.lamps.gi01.pulse(0)
			self.game.lamps.gi02.pulse(0)
			self.game.lamps.gi03.pulse(0)
			self.game.lamps.gi04.pulse(0)
			
	def disable_lamps(self):
		#Disable lamps
		self.game.lamps.blackoutJackpot.disable()
		self.game.lamps.tankCenter.disable()
		#Disable Flashers
		self.game.coils.flasherBlackout.disable()
		self.game.coils.flashersLowerLeft.disable()
		self.game.coils.flasherPursuitL.disable()
		self.game.coils.flasherCursedEarth.disable()
		self.game.coils.flasherGlobe.disable()
		self.game.coils.flashersRtRamp.disable()
		self.game.coils.flasherPursuitR.disable()
		#Disable shared jackpot lights
		#if self.jackpot_shot_num == 2:
			#Subway
		self.game.lamps.multiballJackpot.disable()
		self.game.lamps.pickAPrize.disable()
		self.game.lamps.dropTargetJ.disable()
		self.game.lamps.dropTargetU.disable()
		self.game.lamps.dropTargetD.disable()
		self.game.lamps.dropTargetG.disable()
		self.game.lamps.dropTargetE.disable()
		#elif self.jackpot_shot_num == 3:
		#right Ramp
		self.game.lamps.perp5W.disable()
		self.game.lamps.perp5R.disable()
		self.game.lamps.perp5G.disable()
		self.game.lamps.perp5Y.disable()
		self.game.coils.flasherPursuitR.disable()
		#elif self.jackpot_shot_num == 1:
		#Sniper Tower
		self.game.lamps.perp3W.disable()
		self.game.lamps.perp3R.disable()
		self.game.lamps.perp3G.disable()
		self.game.lamps.perp3Y.disable()
			
	def sw_subwayEnter1_closed(self, sw):
		if self.jackpot_shot_num == 1:
			#Rave in progress and jackpot lit, so add captured raver
			self.subway_missed_switch = 0
			self.capture_raver()
			
	# Ball might jump over first switch.  Use 2nd switch as a catchall.
	def sw_subwayEnter2_closed(self, sw):
		if self.jackpot_shot_num == 1:
			#Rave in progress and jackpot lit, so add captured raver
			if self.subway_missed_switch == 1:
				#switch Missed
				self.capture_raver()
			else:
				self.subway_missed_switch = 1
			
	def sw_rightRampExit_active(self, sw):
		if self.jackpot_shot_num == 2:
			#Rave in progress and jackpot lit, so add captured raver
			self.capture_raver()

	def sw_popperR_active_for_300ms(self, sw):
		if self.jackpot_shot_num == 3:
			#Rave in progress and jackpot lit, so add captured raver
			self.capture_raver()
		
	def sw_centerRampExit_active(self, sw):
		self.completed = True
		#self.game.coils.flasherBlackout.schedule(schedule=0x000F000F, cycle_seconds=0, now=True)
		#self.game.score(10000)
		print "% 10.3f Blackout calling callback" % (time.time())
		self.check_for_completion()
		if self.rave_started == 1:
			#Rave in progress, so add captured raver
			self.capture_raver()
		else:
			#Enter the Rave!!!
			self.blackout_start_rave_seq()
			
	def capture_raver(self):
		self.shots += 1
		#Collect Jackpot
		self.game.score(self.rave_capture_score)
		#Update Status
		self.update_status()
		#Play Audio "Raver Captured"
		self.game.sound.play_voice('capture_raver')
		#Lampshow Placeholder
		#Add bonus time to the clock
		self.timer += self.rave_timer_inc
		self.increment_rave_jackpot()
		self.trip_check()
		self.update_lamps()
		
	def trip_check(self):
		if self.jackpot_shot_num == 1:
			if self.game.switches.dropTargetD.is_inactive():
				self.game.coils.tripDropTarget.pulse(40)
				self.delay(name='trip_check', event_type=None, delay=.400, handler=self.trip_check)	
					
	def check_for_completion(self):
		self.update_status()
		if self.shots == self.shots_required_for_completion:
			self.completed = True
			self.game.score(self.rave_completion_score)

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		font_small = self.game.fonts['tiny7']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer21 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer22 = dmd.TextLayer(128/2, 24, font_small, "center").set_text("Shoot center ramp")
		instruction_layers = [[layer1], [layer21, layer22]]
		return instruction_layers

class Sniper(ChainFeature):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(Sniper, self).__init__(game, priority, 'Sniper')
		filename = curr_file_path + "/dmd/scope.dmd"

		self.countdown_layer = dmd.TextLayer(127, 1, self.game.fonts['tiny7'], "right")
		self.name_layer = dmd.TextLayer(1, 1, self.game.fonts['tiny7'], "left").set_text("Sniper")
		self.score_layer = dmd.TextLayer(127, 10, self.game.fonts['num_14x10'], "right")
		self.status_layer = dmd.TextLayer(127, 26, self.game.fonts['tiny7'], "right")

		if os.path.isfile(filename):
			anim = dmd.Animation().load(filename)
			self.anim_layer = dmd.AnimatedLayer(frames=anim.frames, repeat=True, frame_time=8)
			self.layer = dmd.GroupedLayer(128, 32, [self.anim_layer,self.countdown_layer, self.name_layer, self.score_layer, self.status_layer])
		else:
			self.layer = dmd.GroupedLayer(128, 32, [self.countdown_layer, self.name_layer, self.score_layer, self.status_layer])

		full_voice_path = voice_path + 'sniper/'
		filename = 'jd - missed him.wav'
		self.game.sound.register_sound('sniper - miss', full_voice_path+filename)
		filename = 'jd - drokk.wav'
		self.game.sound.register_sound('sniper - miss', full_voice_path+filename)
		filename = 'jd - grud.wav'
		self.game.sound.register_sound('sniper - miss', full_voice_path+filename)
		filename = 'jd - sniper neutralized.wav'
		self.game.sound.register_sound('sniper - hit', full_voice_path+filename)
		filename = 'jd - take that punk.wav'
		self.game.sound.register_sound('sniper - hit', full_voice_path+filename)
		filename = 'gunshot.wav'
		self.game.sound.register_sound('sniper - shot', full_voice_path+filename)
		time = random.randint(2,7)
		self.delay(name='gunshot', event_type=None, delay=time, handler=self.gunshot)
	def gunshot(self):
		time = random.randint(2,7)
		self.delay(name='gunshot', event_type=None, delay=time, handler=self.gunshot)
		self.game.sound.play_voice('sniper - shot')


	def mode_started(self):
		self.shots = 0
		self.update_status()
		self.update_lamps()

	def update_status(self):
		status = 'Shots made: ' + str(self.shots) + '/' + str(2)
		self.status_layer.set_text(status)

	def mode_stopped(self):
		self.game.lamps.awardSniper.disable()
		self.cancel_delayed('sniper - gunshot')

	def update_lamps(self):
		self.game.lamps.awardSniper.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)

	def sw_popperR_active_for_300ms(self, sw):
		self.shots += 1
		self.game.score(10000)
		filename = curr_file_path + "/dmd/dredd_shoot_at_sniper.dmd"
		if os.path.isfile(filename):
			anim = dmd.Animation().load(filename)
			self.game.base_game_mode.jd_modes.play_animation(anim, 'high', repeat=False, hold=False, frame_time=5)
		self.check_for_completion()

	def check_for_completion(self):
		self.update_status()
		if self.shots == 2:
			self.game.sound.play_voice('sniper - hit')
			self.completed = True
			self.game.score(50000)
			print "% 10.3f Sniper calling callback" % (time.time())
			self.callback()
		else:
			self.game.sound.play_voice('sniper - miss')

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		font_small = self.game.fonts['tiny7']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer21 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer22 = dmd.TextLayer(128/2, 24, font_small, "center").set_text("Shoot Sniper Tower 2 times")
		instruction_layers = [[layer1], [layer21, layer22]]
		return instruction_layers


class BattleTank(ChainFeature):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(BattleTank, self).__init__(game, priority, 'Battle Tank')

		self.num_shots = 0
		full_voice_path = voice_path + 'battle_tank/'
		for i in range(1,11):
			filename = 'unknown tank block ' + str(i) + '.wav'
			self.game.sound.register_sound('tank intro', full_voice_path+filename)

		filename = 'its damaged but still going.wav'
		self.game.sound.register_sound('tank hit 1', full_voice_path+filename)
		filename = 'tank hit 1 more shot.wav'
		self.game.sound.register_sound('tank hit 2', full_voice_path+filename)
		filename = 'tank down.wav'
		self.game.sound.register_sound('tank hit 3', full_voice_path+filename)

	def mode_started(self):
		self.shots = {'left':False,'center':False,'right':False}
		self.update_status()
		self.update_lamps()
		self.game.sound.play_voice('tank intro')

	def update_status(self):
		status = 'Shots made: ' + str(self.num_shots) + '/' + str(len(self.shots))
		self.status_layer.set_text(status)
		

	def mode_stopped(self):
		self.game.lamps.tankCenter.disable()
		self.game.lamps.tankLeft.disable()
		self.game.lamps.tankRight.disable()

	def update_lamps(self):
		if not self.shots['center']:
			self.game.lamps.tankCenter.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
		if not self.shots['left']:
			self.game.lamps.tankLeft.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)
		if not self.shots['right']:
			self.game.lamps.tankRight.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)

	def sw_topRightOpto_active(self, sw):
		if not self.shots['left']:
			if self.game.switches.leftRollover.time_since_change() < 1:
				self.game.lamps.tankLeft.disable()
				self.shots['left'] = True
				self.game.score(10000)
				self.num_shots += 1
				self.check_for_completion()

	def sw_centerRampExit_active(self, sw):
		if not self.shots['center']:
			self.game.lamps.tankCenter.disable()
			self.shots['center'] = True
			self.game.score(10000)
			self.num_shots += 1
			self.check_for_completion()

	def sw_threeBankTargets_active(self, sw):
		if not self.shots['right']:
			self.game.lamps.tankRight.disable()
			self.shots['right'] = True
			self.game.score(10000)
			self.num_shots += 1
			self.check_for_completion()

	def check_for_completion(self):
		self.update_status()
		for i in range(1,4):
			self.game.sound.stop('tank hit ' + str(i))
		self.game.sound.play_voice('tank hit ' + str(self.num_shots))
		if self.shots['right'] and self.shots['left'] and self.shots['center']:
			self.completed = True
			self.game.score(50000)
			print "% 10.3f BattleTank calling callback" % (time.time())
			self.callback()

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		font_small = self.game.fonts['tiny7']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer21 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer22 = dmd.TextLayer(128/2, 24, font_small, "center").set_text("Shoot all 3 battle tank shots")
		instruction_layers = [[layer1], [layer21, layer22]]
		return instruction_layers


class Meltdown(ChainFeature):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(Meltdown, self).__init__(game, priority, 'Meltdown')
		difficulty = self.game.user_settings['Gameplay']['Chain feature difficulty']
		if difficulty == 'easy':
			self.shots_required_for_completion = 3
		elif difficulty == 'medium':
			self.shots_required_for_completion = 5
		else:
			self.shots_required_for_completion = 7

		full_voice_path = voice_path + 'meltdown/'
		for i in range(1,5):
			filename = 'reactor ' + str(i) + ' stabilized.wav'
			self.game.sound.register_sound('meltdown ' + str(i), full_voice_path+filename)

		filename = 'all reactors stabilized.wav'
		self.game.sound.register_sound('meltdown 5', full_voice_path+filename)

		filename = 'power towers going critical.wav'
		self.game.sound.register_sound('meltdown intro', full_voice_path+filename)

	def mode_started(self):
		self.shots = 0
		self.update_status()
		self.update_lamps()
		self.game.sound.play_voice('meltdown intro')

	def update_status(self):
		status = 'Shots made: ' + str(self.shots) + '/' + str(self.shots_required_for_completion)
		self.status_layer.set_text(status)
		

	def mode_stopped(self):
		self.game.lamps.stopMeltdown.disable()

	def update_lamps(self):
		self.game.lamps.stopMeltdown.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)

	def sw_captiveBall1_active(self, sw):
		self.shots += 1
		self.check_for_completion()
		self.game.score(10000)

	def sw_captiveBall2_active(self, sw):
		self.shots += 1
		self.check_for_completion()
		self.game.score(10000)

	def sw_captiveBall3_active(self, sw):
		self.shots += 1
		self.check_for_completion()
		self.game.score(10000)

	def check_for_completion(self):
		self.update_status()


		for i in range(1,6):
			self.game.sound.stop('meltdown ' + str(i))	

		if self.shots <= 5:
			self.game.sound.play_voice('meltdown ' + str(self.shots))
		else:
			self.game.sound.play_voice('meltdown 5')
		if self.shots >= self.shots_required_for_completion:
			self.completed = True
			self.game.score(50000)
			print "% 10.3f Meltdown calling callback" % (time.time())
			self.callback()

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		font_small = self.game.fonts['tiny7']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer21 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer22 = dmd.TextLayer(128/2, 24, font_small, "center").set_text("Activate " + str(self.shots_required_for_completion) + " captive ball switches")
		instruction_layers = [[layer1], [layer21, layer22]]
		return instruction_layers


class Impersonator(ChainFeature):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(Impersonator, self).__init__(game, priority, 'Impersonator')
		difficulty = self.game.user_settings['Gameplay']['Chain feature difficulty']
		if difficulty == 'easy':
			self.shots_required_for_completion = 3
		elif difficulty == 'medium':
			self.shots_required_for_completion = 5
		else:
			self.shots_required_for_completion = 7

		full_voice_path = voice_path + 'bad_impersonator/'

		for i in range(1,6):
			filename = 'ouch ' + str(i) + '.wav'
			self.game.sound.register_sound('bi - ouch', full_voice_path+filename)

		for i in range(1,6):
			filename = 'song ' + str(i) + '.wav'
			self.game.sound.register_sound('bi - song', full_voice_path+filename)

		for i in range(1,6):
			filename = 'boo ' + str(i) + '.wav'
			self.game.sound.register_sound('bi - boo', full_voice_path+filename)

		for i in range(1,5):
			filename = 'Shut Up ' + str(i) + '.aif'
			self.game.sound.register_sound('bi - shutup', full_voice_path+filename)

		filename = 'bad impersonation in progress.wav'
		self.game.sound.register_sound('bad impersonator', full_voice_path+filename)

		self.sound_active = False

	def play_music(self):
		pass

	def mode_started(self):
		self.shots = 0
		self.delay(name='moving_target', event_type=None, delay=1, handler=self.moving_target)
		if self.game.switches.dropTargetJ.is_active() or self.game.switches.dropTargetU.is_active() or self.game.switches.dropTargetD.is_active() or self.game.switches.dropTargetG.is_active() or self.game.switches.dropTargetE.is_active(): 
			self.game.coils.resetDropTarget.pulse(40)
		self.update_status()
		self.update_lamps()
		time = self.game.sound.play('bad impersonator')
		self.delay(name='song_restart', event_type=None, delay=time+0.5, handler=self.song_restart)
		self.delay(name='boo_restart', event_type=None, delay=time+4, handler=self.boo_restart)
		self.delay(name='shutup_restart', event_type=None, delay=time+3, handler=self.shutup_restart)

	def song_restart(self):
		self.game.sound.play('bi - song')
		self.delay(name='song_restart', event_type=None, delay=6, handler=self.song_restart)

	def boo_restart(self):
		time = random.randint(2,7)
		self.game.sound.play('bi - boo')
		self.delay(name='boo_restart', event_type=None, delay=time, handler=self.boo_restart)
	def shutup_restart(self):
		time = random.randint(2,7)
		self.game.sound.play('bi - shutup')
		self.delay(name='shutup_restart', event_type=None, delay=time, handler=self.shutup_restart)

	def update_status(self):
		if self.shots > self.shots_required_for_completion:
			extra_shots = self.shots - self.shots_required_for_completion
			status = 'Shots made: ' + str(extra_shots) + ' extra'
		else:
			status = 'Shots made: ' + str(self.shots) + '/' + str(self.shots_required_for_completion)
		self.status_layer.set_text(status)
		

	def mode_stopped(self):
		self.game.lamps.awardBadImpersonator.disable()
		self.game.lamps.dropTargetJ.disable()
		self.game.lamps.dropTargetU.disable()
		self.game.lamps.dropTargetD.disable()
		self.game.lamps.dropTargetG.disable()
		self.game.lamps.dropTargetE.disable()
		self.cancel_delayed('moving_target')
		self.cancel_delayed('song_restart')
		self.cancel_delayed('boo_restart')
		self.cancel_delayed('shutup_restart')
		self.cancel_delayed('end_sound')
		self.game.sound.stop('bi - song')
		self.game.sound.stop('bi - boo')

	def update_lamps(self):
		self.game.lamps.awardBadImpersonator.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)

	def end_sound(self):
		self.sound_active = False

	def check_for_completion(self):
		self.game.sound.stop('bi - song')
		if not self.sound_active:
			self.sound_active = True
			self.game.sound.play('bi - ouch')
			self.delay(name='end_sound', event_type=None, delay=1, handler=self.end_sound)
	
		self.update_status()
		if self.shots == self.shots_required_for_completion:
			self.completed = True
			self.game.score(50000)

	def sw_dropTargetJ_active(self,sw):
		if self.timer%6 == 0:
			self.shots += 1
			self.game.score(10000)
			self.check_for_completion()
		self.game.coils.resetDropTarget.pulse(40)

	def sw_dropTargetU_active(self,sw):
		if self.timer%6 == 0 or self.timer%6 == 1 or self.timer%6 == 5:
			self.shots += 1
			self.game.score(10000)
			self.check_for_completion()
		self.game.coils.resetDropTarget.pulse(40)

	def sw_dropTargetD_active(self,sw):
		if self.timer%6 == 2 or self.timer%6 == 4 or self.timer%6 == 1 or self.timer%6 == 5:
			self.shots += 1
			self.game.score(10000)
			self.check_for_completion()
		self.game.coils.resetDropTarget.pulse(40)

	def sw_dropTargetG_active(self,sw):
		if self.timer%6 == 2 or self.timer%6 == 3 or self.timer%6 == 4:
			self.shots += 1
			self.game.score(10000)
			self.check_for_completion()
		self.game.coils.resetDropTarget.pulse(40)

	def sw_dropTargetE_active(self,sw):
		if self.timer%6 == 3:
			self.shots += 1
			self.game.score(10000)
			self.check_for_completion()
		self.game.coils.resetDropTarget.pulse(40)

	def moving_target(self):
		#self.timer += 1
		self.game.lamps.dropTargetJ.disable()
		self.game.lamps.dropTargetU.disable()
		self.game.lamps.dropTargetD.disable()
		self.game.lamps.dropTargetG.disable()
		self.game.lamps.dropTargetE.disable()
		if self.timer%6 == 0:
			self.game.lamps.dropTargetJ.pulse(0)
			self.game.lamps.dropTargetU.pulse(0)
		elif self.timer%6 == 1 or self.timer%6==5:
			self.game.lamps.dropTargetU.pulse(0)
			self.game.lamps.dropTargetD.pulse(0)
		elif self.timer%6 == 2 or self.timer%6==4:
			self.game.lamps.dropTargetD.pulse(0)
			self.game.lamps.dropTargetG.pulse(0)
		elif self.timer%6 == 3:
			self.game.lamps.dropTargetG.pulse(0)
			self.game.lamps.dropTargetE.pulse(0)
		self.delay(name='moving_target', event_type=None, delay=1, handler=self.moving_target)

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		font_small = self.game.fonts['tiny7']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer21 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer22 = dmd.TextLayer(128/2, 24, font_small, "center").set_text("Shoot " + str(self.shots_required_for_completion) + " lit drop targets")
		instruction_layers = [[layer1], [layer21, layer22]]
		return instruction_layers

		

class Safecracker(ChainFeature):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(Safecracker, self).__init__(game, priority, 'Safe Cracker')
		difficulty = self.game.user_settings['Gameplay']['Chain feature difficulty']
		if difficulty == 'easy':
			self.shots_required_for_completion = 2
		elif difficulty == 'medium':
			self.shots_required_for_completion = 3
		else:
			self.shots_required_for_completion = 4

		full_voice_path = voice_path + 'safecracker/'
		filename = 'hurry up.wav'
		self.game.sound.register_sound('bad guys', full_voice_path+filename)
		filename = 'running out of time.wav'
		self.game.sound.register_sound('bad guys', full_voice_path+filename)
		time = random.randint(10,20)
		self.delay(name='bad guys', event_type=None, delay=time, handler=self.bad_guys)

		filename = 'jd - youre done.wav'
		self.game.sound.register_sound('complete', full_voice_path+filename)
		filename = 'surrounded.wav'
		self.game.sound.register_sound('shot', full_voice_path+filename)
		filename = 'great shot.wav'
		self.game.sound.register_sound('shot', full_voice_path+filename)
		filename = 'jd - excellent.wav'
		self.game.sound.register_sound('shot', full_voice_path+filename)
		filename = 'jd - do it again.wav'
		self.game.sound.register_sound('shot', full_voice_path+filename)

	def bad_guys(self):
		time = random.randint(5,10)
		self.delay(name='bad guys', event_type=None, delay=time, handler=self.bad_guys)
		self.game.sound.play_voice('bad guys')

	def mode_started(self):
		self.shots = 0
		if self.game.switches.dropTargetJ.is_active() or self.game.switches.dropTargetU.is_active() or self.game.switches.dropTargetD.is_active() or self.game.switches.dropTargetG.is_active() or self.game.switches.dropTargetE.is_active():
			self.game.coils.resetDropTarget.pulse(40)
		self.delay(name='trip_check', event_type=None, delay=1, handler=self.trip_check)
		self.update_status()
		self.update_lamps()

	def update_lamps(self):
		self.game.lamps.awardSafecracker.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)

	def update_status(self):
		status = 'Shots made: ' + str(self.shots) + '/' + str(self.shots_required_for_completion)
		self.status_layer.set_text(status)
		

	def mode_stopped(self):
		self.cancel_delayed('trip_check')
		self.cancel_delayed('bad guys')
		self.game.lamps.awardSafecracker.disable()
		if self.game.switches.dropTargetJ.is_active() or self.game.switches.dropTargetU.is_active() or self.game.switches.dropTargetD.is_active() or self.game.switches.dropTargetG.is_active() or self.game.switches.dropTargetE.is_active():
			self.game.coils.resetDropTarget.pulse(40)

	def update_lamps(self):
		self.game.lamps.awardSafecracker.schedule(schedule=0x00FF00FF, cycle_seconds=0, now=True)

	def sw_subwayEnter2_active(self, sw):
		self.shots += 1
		self.check_for_completion()
		self.game.score(10000)

	def sw_dropTargetD_inactive_for_400ms(self, sw):
		self.game.coils.tripDropTarget.pulse(30)

	def check_for_completion(self):
		self.update_status()
		if self.shots == self.shots_required_for_completion:
			self.game.sound.play_voice('complete')
			self.completed = True
			self.game.score(50000)
			print "% 10.3f Safecracker calling callback" % (time.time())
			self.callback()
		else:
			self.game.sound.play_voice('shot')

	def trip_check(self):
		if self.game.switches.dropTargetD.is_inactive():
			self.game.coils.tripDropTarget.pulse(40)
			self.delay(name='trip_check', event_type=None, delay=.400, handler=self.trip_check)

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		font_small = self.game.fonts['tiny7']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer21 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer22 = dmd.TextLayer(128/2, 24, font_small, "center").set_text("Shoot the subway " + str(self.shots_required_for_completion) + " times")
		instruction_layers = [[layer1], [layer21, layer22]]
		return instruction_layers


class ManhuntMillions(ChainFeature):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(ManhuntMillions, self).__init__(game, priority, 'Manhunt')
		difficulty = self.game.user_settings['Gameplay']['Chain feature difficulty']
		if difficulty == 'easy':
			self.shots_required_for_completion = 2
		elif difficulty == 'medium':
			self.shots_required_for_completion = 3
		else:
			self.shots_required_for_completion = 4

		full_voice_path = voice_path + 'manhunt/'
		filename = 'bank robbers trying to escape judgement.wav'
		self.game.sound.register_sound('mm - intro', full_voice_path+filename)
		filename = 'aahh.wav'
		self.game.sound.register_sound('mm - shot', full_voice_path+filename)
		filename = 'jd - i got one.wav'
		self.game.sound.register_sound('mm - shot', full_voice_path+filename)
		filename = 'jd - that will stop him.wav'
		self.game.sound.register_sound('mm - shot', full_voice_path+filename)
		filename = 'jd - fugutives captured.wav'
		self.game.sound.register_sound('mm - done', full_voice_path+filename)

	def mode_started(self):
		self.shots = 0
		self.update_status()
		self.update_lamps()
		self.game.sound.play_voice('mm - intro')

	def update_lamps(self):
		self.game.coils.flasherPursuitL.schedule(schedule=0x000F000F, cycle_seconds=0, now=True)

	def update_status(self):
		status = 'Shots made: ' + str(self.shots) + '/' + str(self.shots_required_for_completion)
		self.status_layer.set_text(status)
		

	def mode_stopped(self):
		self.game.coils.flasherPursuitL.disable()

	# Award shot if ball diverted for multiball.  Ensure it was a fast
	# shot rather than one that just trickles in.
	def sw_leftRampToLock_active(self, sw):
		if self.game.switches.leftRampEnter.time_since_change() < 0.5:
			self.shots += 1
			self.game.score(10000)
			self.check_for_completion()

	def sw_leftRampExit_active(self, sw):
		self.shots += 1
		self.check_for_completion()
		self.game.score(10000)

	def check_for_completion(self):
		self.update_status()
		if self.shots == self.shots_required_for_completion:
			self.game.sound.play_voice('mm - done')
			self.completed = True
			self.game.score(50000)
			print "% 10.3f Manhunt calling callback" % (time.time())
			self.callback()
		else:
			self.game.sound.play_voice('mm - shot')

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		font_small = self.game.fonts['tiny7']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer21 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer22 = dmd.TextLayer(128/2, 24, font_small, "center").set_text("Shoot the left ramp " + str(self.shots_required_for_completion) + " times")
		instruction_layers = [[layer1], [layer21, layer22]]
		return instruction_layers


class Stakeout(ChainFeature):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(Stakeout, self).__init__(game, priority, 'Stakeout')
		difficulty = self.game.user_settings['Gameplay']['Chain feature difficulty']
		if difficulty == 'easy':
			self.shots_required_for_completion = 3
		elif difficulty == 'medium':
			self.shots_required_for_completion = 4
		else:
			self.shots_required_for_completion = 5

		full_voice_path = voice_path + 'stakeout/'

		filename = 'jd - over there 1.wav'
		self.game.sound.register_sound('so - over there', full_voice_path+filename)
		filename = 'jd - over there 2.wav'
		self.game.sound.register_sound('so - over there', full_voice_path+filename)
		filename = 'jd - we have you surrounded.wav'
		self.game.sound.register_sound('so - surrounded', full_voice_path+filename)
		filename = 'jd - move in now.wav'
		self.game.sound.register_sound('so - move in', full_voice_path+filename)
		filename = 'jd - thats it take em down.wav'
		self.game.sound.register_sound('so - move in', full_voice_path+filename)
		filename = 'jd - are we sure we have the right place.wav'
		self.game.sound.register_sound('so - boring', full_voice_path+filename)
		filename = 'jd - this is boring.wav'
		self.game.sound.register_sound('so - boring', full_voice_path+filename)
		filename = 'most boring stakeout ever.wav'
		self.game.sound.register_sound('so - boring', full_voice_path+filename)
		filename = 'wake me when something happens.wav'
		self.game.sound.register_sound('so - boring', full_voice_path+filename)

	def mode_started(self):
		self.shots = 0
		self.update_status()
		self.update_lamps()
		self.delay(name='boring', event_type=None, delay=15, handler=self.boring_expired)

	def boring_expired(self):
		self.game.sound.play_voice('so - boring')
		self.delay(name='boring', event_type=None, delay=5, handler=self.boring_expired)

	def update_lamps(self):
		self.game.coils.flasherPursuitR.schedule(schedule=0x000F000F, cycle_seconds=0, now=True)

	def update_status(self):
		status = 'Shots made: ' + str(self.shots) + '/' + str(self.shots_required_for_completion)
		self.status_layer.set_text(status)
		

	def mode_stopped(self):
		self.cancel_delayed('boring')
		self.game.coils.flasherPursuitR.disable()

	def sw_rightRampExit_active(self, sw):
		self.shots += 1
		self.check_for_completion()
		self.game.score(10000)

	def check_for_completion(self):
		self.cancel_delayed('boring')
		self.update_status()
		self.game.sound.stop('so - boring')
		if self.shots == self.shots_required_for_completion:
			self.completed = True
			self.game.score(50000)
			self.callback()
		elif self.shots == 1:
			self.game.sound.play_voice('so - over there')
		elif self.shots == 2:
			self.game.sound.play_voice('so - surrounded')
		elif self.shots == 3:
			self.game.sound.play_voice('so - move in')
	

	def get_instruction_layers(self):
		font = self.game.fonts['jazz18']
		font_small = self.game.fonts['tiny7']
		layer1 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer21 = dmd.TextLayer(128/2, 7, font, "center").set_text(self.name)
		layer22 = dmd.TextLayer(128/2, 24, font_small, "center").set_text("Shoot the right ramp " + str(self.shots_required_for_completion) + " times")
		instruction_layers = [[layer1], [layer21, layer22]]
		return instruction_layers

	
