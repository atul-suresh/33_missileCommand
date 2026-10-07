"""Deterministic checks, separate from gameplay. Run: python3 Lab-4/tests/test_game.py."""
import ast
import importlib.util
import math
import os
from pathlib import Path
import random
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

try:
    import pygame
    pygame.init()
    USING_DOUBLES = False
except ModuleNotFoundError:
    USING_DOUBLES = True

    class Vector2:
        """Small vector test double; never imported by production gameplay."""
        def __init__(self, x, y=None):
            if y is None:
                x, y = (x.x, x.y) if isinstance(x, Vector2) else x
            self.x, self.y = float(x), float(y)
        def __add__(self, other):
            return Vector2(self.x + other.x, self.y + other.y)
        def __sub__(self, other):
            return Vector2(self.x - other.x, self.y - other.y)
        def __mul__(self, scale):
            return Vector2(self.x * scale, self.y * scale)
        def length(self):
            return math.hypot(self.x, self.y)
        def normalize(self):
            length = self.length()
            return Vector2(self.x / length, self.y / length)
        def distance_squared_to(self, other):
            other = Vector2(other)
            return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    pygame = SimpleNamespace(Vector2=Vector2, font=SimpleNamespace(Font=lambda *args: None),
                             draw=SimpleNamespace(rect=lambda *args: None, polygon=lambda *args: None,
                                                  line=lambda *args: None, circle=lambda *args: None))
    sys.modules['pygame'] = pygame

GAME_PATH = Path(__file__).resolve().parents[1] / 'game.py'
spec = importlib.util.spec_from_file_location('lab4_game', GAME_PATH)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

class Label:
    def __init__(self, text):
        self.text = text
    def get_rect(self, **kwargs):
        return kwargs

class Font:
    def render(self, text, *args):
        return Label(text)

class Screen:
    def __init__(self):
        self.labels = []
    def fill(self, color):
        pass
    def blit(self, label, position):
        self.labels.append((label.text, position))

class GameChecks(unittest.TestCase):
    def setUp(self):
        random.seed(33)
        self.game = g.Game()
        self.game.font = Font()
        # Keep test state stable: no spawning or incidental wave completion.
        self.game.spawn_timer = 100
        self.game.to_spawn = 1

    def missile_at(self, target, pos):
        missile = g.Missile(target, 51)
        missile.pos = pygame.Vector2(pos)
        missile.velocity = pygame.Vector2(0, 0)
        return missile

    def labels(self):
        screen = Screen()
        with patch.object(pygame.draw, 'rect'), patch.object(pygame.draw, 'polygon'), \
             patch.object(pygame.draw, 'line'), patch.object(pygame.draw, 'circle'):
            self.game.draw(screen)
        return screen.labels

    def warnings(self):
        return [pos for text, pos in self.labels() if text == 'CITY DESTROYED!']

    def test_battery_selection_and_one_ammo_per_launch(self):
        for scenario in ('available', 'depleted', 'destroyed', 'mixed_unavailable', 'empty'):
            with self.subTest(scenario=scenario):
                self.setUp()
                batteries = self.game.batteries
                expected = batteries[0]
                if scenario == 'depleted':
                    batteries[0].ammo = 0
                    expected = batteries[1]
                elif scenario == 'destroyed':
                    batteries[0].alive = False
                    expected = batteries[1]
                elif scenario == 'mixed_unavailable':
                    batteries[0].ammo = 0
                    batteries[1].alive = False
                    batteries[2].ammo = -1
                    expected = None
                elif scenario == 'empty':
                    batteries.clear()
                    expected = None
                before = [b.ammo for b in batteries]
                target = pygame.Vector2(60, 100)
                self.assertIs(self.game.nearest_battery(target), expected)
                self.game.launch(target)
                after = before[:]
                if expected is not None:
                    after[batteries.index(expected)] -= 1
                    self.assertEqual(len(self.game.interceptors), 1)
                    interceptor = self.game.interceptors[0]
                    self.assertEqual(interceptor.origin.distance_squared_to(expected.pos), 0)
                    self.assertEqual(interceptor.target.distance_squared_to(target), 0)
                else:
                    self.assertEqual(self.game.interceptors, [])
                self.assertEqual([b.ammo for b in batteries], after)

    def test_last_ammo_then_fallback(self):
        self.game.batteries[0].ammo = 1
        self.game.launch((60, 100))
        self.game.launch((60, 100))
        self.assertEqual([b.ammo for b in self.game.batteries], [0, 9, 10])
        self.assertEqual(len(self.game.interceptors), 2)

    def test_launch_target_and_state_guards(self):
        self.game.launch((60, g.GROUND_Y - 19))
        self.assertEqual(self.game.interceptors, [])
        self.game.state = 'lose'
        self.game.launch((60, 100))
        self.assertEqual([b.ammo for b in self.game.batteries], [10, 10, 10])
        self.game.state = 'play'
        self.game.launch((60, g.GROUND_Y - 20))
        self.assertEqual(len(self.game.interceptors), 1)

    def test_color_endpoints_midpoint_and_clamping(self):
        for progress, expected in [(-2, (255,255,255)), (0, (255,255,255)),
                                   (1/3, (255,255,0)), (.5, (255,192,0)),
                                   (2/3, (255,128,0)), (1, (255,0,0)), (2, (255,0,0))]:
            self.assertEqual(g.explosion_color(progress), expected)

    def test_color_integer_bounds_and_smoothness(self):
        colors = [g.explosion_color(i/1000) for i in range(1001)]
        self.assertTrue(all(type(v) is int and 0 <= v <= 255 for c in colors for v in c))
        self.assertTrue(all(max(abs(a-b) for a,b in zip(c,d)) <= 1 for c,d in zip(colors,colors[1:])))

    def test_interceptor_reaches_exact_target_without_oscillation(self):
        interceptor = g.Interceptor((60, g.GROUND_Y), (60, g.GROUND_Y-31))
        arrived = False
        for _ in range(100):
            if interceptor.update(.05):
                arrived = True
                break
        self.assertTrue(arrived, '21-pixel steps must not oscillate around a target 31 pixels away')
        self.assertEqual(interceptor.pos.distance_squared_to(interceptor.target), 0)

    def test_interceptor_does_not_detonate_short_of_target(self):
        interceptor = g.Interceptor((0, 0), (5, 0))
        self.assertFalse(interceptor.update(.001), '0.42-pixel movement cannot reach a 5-pixel target')
        self.assertAlmostEqual(interceptor.pos.x, .42)
        self.assertTrue(interceptor.update(.05))
        self.assertEqual(interceptor.pos.distance_squared_to(interceptor.target), 0)

    def test_interceptor_already_at_target(self):
        interceptor = g.Interceptor((20, 20), (20, 20))
        self.assertTrue(interceptor.update(0))

    def test_game_detonates_interceptor_at_target(self):
        self.game.launch((60, g.GROUND_Y-31))
        self.game.update(.05)
        self.game.update(.05)
        self.assertEqual(self.game.interceptors, [])
        self.assertEqual(len(self.game.explosions), 1)
        self.assertEqual(self.game.explosions[0].pos.distance_squared_to((60,g.GROUND_Y-31)), 0)

    def test_explosion_timing_and_radius(self):
        explosion = g.Explosion((100, 100))
        self.assertEqual(explosion.radius, 0)
        explosion.age = g.EXPLOSION_TIME/2
        self.assertEqual(explosion.radius, g.EXPLOSION_MAX)
        self.assertFalse(explosion.done)
        explosion.age = g.EXPLOSION_TIME
        self.assertEqual(explosion.radius, 0)
        self.assertTrue(explosion.done)
        self.game.explosions = [explosion]
        self.game.update(0)
        self.assertEqual(self.game.explosions, [])

    def test_collision_uses_missile_head_and_scores_once(self):
        explosion = g.Explosion((100,100))
        explosion.age = g.EXPLOSION_TIME/2
        self.game.explosions = [explosion]
        self.game.missiles = [self.missile_at(self.game.cities[0],pos) for pos in ((100,100),(140,100),(146,100))]
        self.game.update(0)
        self.assertEqual(len(self.game.missiles), 1)
        self.assertEqual(self.game.score, 50)
        self.game.update(0)
        self.assertEqual(self.game.score, 50)

    def test_collision_respects_current_not_maximum_radius(self):
        explosion = g.Explosion((100,100))
        explosion.age = .1
        self.game.explosions = [explosion]
        missile = self.missile_at(self.game.cities[0],(110,100))
        self.game.missiles = [missile]
        self.game.update(0)
        self.assertEqual(self.game.missiles, [missile])

    def test_city_feedback_new_hit_repeat_hit_and_battery(self):
        city = self.game.cities[0]
        hit = self.missile_at(city,city.pos)
        with patch.object(g,'on_city_destroyed',wraps=g.on_city_destroyed) as callback:
            self.game.impact(hit)
            self.assertFalse(city.alive)
            self.assertEqual(city.destruction_timer, 2)
            self.assertEqual(self.warnings(), [{'center':(city.pos.x,g.GROUND_Y-50)}])
            self.game.update(.5)
            self.game.impact(hit)
            self.game.impact(self.missile_at(self.game.batteries[0],self.game.batteries[0].pos))
            self.assertEqual(callback.call_count, 1)
            self.assertEqual(city.destruction_timer, 1.5)
            self.assertFalse(self.game.batteries[0].alive)

    def test_feedback_expiration(self):
        self.game.impact(self.missile_at(self.game.cities[0],self.game.cities[0].pos))
        self.game.update(1.5)
        self.assertEqual(len(self.warnings()), 1)
        self.game.update(.5)
        self.assertEqual(self.warnings(), [])
        self.game.update(.5)
        self.assertEqual(self.game.cities[0].destruction_timer, 0)

    def test_missile_moves_and_impacts_its_target(self):
        city = self.game.cities[0]
        missile = self.missile_at(city,(city.pos.x,g.GROUND_Y-10))
        missile.velocity = pygame.Vector2(0,100)
        self.game.missiles = [missile]
        self.game.update(.01)
        self.assertTrue(city.alive)
        self.assertAlmostEqual(missile.pos.y,g.GROUND_Y-9)
        self.game.update(.05)
        self.assertFalse(city.alive)
        self.assertEqual(self.game.missiles, [])
        self.assertEqual(self.game.explosions[-1].max_radius,30)

    def test_wave_progression_bonus_and_ammo_refill(self):
        self.game.cities[0].alive = False
        self.game.batteries[0].alive = False
        for battery,ammo in zip(self.game.batteries,(3,4,5)):
            battery.ammo = ammo
        self.game.to_spawn = 0
        self.game.update(0)
        self.assertEqual(self.game.wave, 2)
        self.assertEqual(self.game.score, 500+5*12)
        self.assertEqual(self.game.to_spawn, 10)
        self.assertTrue(all(b.alive and b.ammo == 10 for b in self.game.batteries))
        self.assertFalse(self.game.cities[0].alive)

    def test_spawn_uses_only_alive_targets(self):
        for city in self.game.cities:
            city.alive = False
        for battery in self.game.batteries[1:]:
            battery.alive = False
        self.game.to_spawn = 2
        self.game.spawn_timer = 0
        self.game.update(0)
        self.assertEqual(len(self.game.missiles),1)
        self.assertIs(self.game.missiles[0].target,self.game.batteries[0])
        self.assertEqual(self.game.to_spawn,1)

    def test_repair_each_successive_milestone_once(self):
        self.assertEqual(g.city_repair_threshold(),2000)
        for city in self.game.cities[:3]:
            city.alive = False
        self.game.score = 1999
        self.game.update(0)
        self.assertEqual(sum(c.alive for c in self.game.cities),3)
        for milestone in (2000,4000,6000):
            self.game.score = milestone
            before = sum(c.alive for c in self.game.cities)
            self.game.update(0)
            self.assertEqual(sum(c.alive for c in self.game.cities),before+1)
            self.assertEqual(self.game.repairs_awarded,milestone//2000)
            self.game.update(0)
            self.assertEqual(sum(c.alive for c in self.game.cities),before+1)

    def test_repair_no_destroyed_city_consumes_milestone(self):
        self.game.score = 2000
        self.game.update(0)
        self.assertEqual(self.game.repairs_awarded,1)
        self.game.cities[0].alive = False
        self.game.update(0)
        self.assertFalse(self.game.cities[0].alive)

    def test_repair_processes_every_crossed_milestone(self):
        for city in self.game.cities[:3]:
            city.alive = False
        self.game.score = 6000
        self.game.update(0)
        self.assertEqual(sum(c.alive for c in self.game.cities),6)
        self.assertEqual(self.game.repairs_awarded,3)
        self.game.update(0)
        self.assertEqual(sum(c.alive for c in self.game.cities),6)

    def test_real_scoring_crosses_milestone_then_repairs(self):
        self.game.cities[0].alive = False
        self.game.score = 1975
        explosion = g.Explosion((100,100))
        explosion.age = .6
        self.game.explosions = [explosion]
        self.game.missiles = [self.missile_at(self.game.cities[1],(100,100))]
        self.game.update(0)
        self.assertEqual(self.game.score,2000)
        self.assertFalse(self.game.cities[0].alive)
        self.game.update(0)
        self.assertTrue(self.game.cities[0].alive)
        self.assertEqual(self.game.repairs_awarded,1)

    def test_last_city_game_over_feedback_and_no_repair(self):
        for city in self.game.cities[:-1]:
            city.alive = False
        last = self.game.cities[-1]
        self.game.missiles = [self.missile_at(last,last.pos)]
        self.game.update(.05)
        self.assertEqual(self.game.state,'lose')
        self.assertEqual(len(self.warnings()),1)
        self.assertTrue(any(text == 'ALL CITIES LOST - Press R' for text,_ in self.labels()))
        self.game.score = 6000
        self.game.update(1)
        self.assertFalse(any(c.alive for c in self.game.cities))
        self.assertEqual(self.game.repairs_awarded,0)
        self.assertEqual(len(self.warnings()),1)
        self.game.update(1)
        self.assertEqual(self.warnings(),[])
        self.assertEqual(self.game.state,'lose')

    def test_reset_clears_all_state_and_repair_bookkeeping(self):
        self.game.impact(self.missile_at(self.game.cities[0],self.game.cities[0].pos))
        self.game.launch((60,100))
        self.game.score = 4000
        self.game.repairs_awarded = 2
        self.game.wave = 5
        self.game.state = 'lose'
        self.game.reset()
        self.assertEqual((self.game.score,self.game.wave,self.game.state,self.game.repairs_awarded),(0,1,'play',0))
        self.assertTrue(all(c.alive and c.destruction_timer == 0 for c in self.game.cities))
        self.assertTrue(all(b.alive and b.ammo == 10 for b in self.game.batteries))
        self.assertEqual((self.game.missiles,self.game.interceptors,self.game.explosions),([],[],[]))
        self.assertEqual(self.game.to_spawn,8)
        self.assertEqual(self.warnings(),[])
        tree = ast.parse(GAME_PATH.read_text())
        self.assertTrue(any(isinstance(node,ast.Attribute) and node.attr == 'K_r' for node in ast.walk(tree)))

    def test_draw_uses_explosion_color_and_radius(self):
        explosion = g.Explosion((100,100))
        explosion.age = .6
        self.game.explosions = [explosion]
        with patch.object(pygame.draw,'rect'), patch.object(pygame.draw,'polygon'), \
             patch.object(pygame.draw,'line'), patch.object(pygame.draw,'circle') as circle:
            self.game.draw(Screen())
        args = circle.call_args.args
        self.assertEqual(args[1],(255,192,0))
        self.assertEqual(args[3],45)

if __name__ == '__main__':
    print('MODE: real Pygame vectors' if not USING_DOUBLES else 'MODE: vector test double (Pygame unavailable)',flush=True)
    print('Drawing assertions use spies; this suite is not gameplay-video evidence.',flush=True)
    unittest.main(verbosity=2)
