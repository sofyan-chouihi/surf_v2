"""
@author: Chouihi Sofyan - green813
Module: test_project
Description: Suite de tests unitaires.
"""

import unittest
import pandas as pd
from indicators import Tide, Swell
from spots import Spot
from analysis import PenfoulScoreVisitor, BestSession


class TestProject(unittest.TestCase):
    def test_tide_up(self):
        fake_tide_up = Tide(pd.Timestamp.now(), 2)
        fake_tide_up.tide_speed = 0.5

        fake_spot = Spot("Test", 0.0, 0.0)
        fake_spot.add_indicator(fake_tide_up)
        fake_spot.state_tide()

        state = fake_spot.marine_indicators["tide"][1].tide_state
        self.assertEqual(state, "montante")

    def test_tide_down(self):
        fake_tide_down = Tide(pd.Timestamp.now(), 2)
        fake_tide_down.tide_speed = -0.5

        fake_spot = Spot("Test", 0.0, 0.0)
        fake_spot.add_indicator(fake_tide_down)
        fake_spot.state_tide()

        state = fake_spot.marine_indicators["tide"][1].tide_state
        self.assertEqual(state, "descendante")

    def test_swell_good(self):
        visitor = PenfoulScoreVisitor(pd.DataFrame())
        good_swell = Swell(pd.Timestamp.now(), 1, 10, 270)
        score = good_swell.accept(visitor)
        self.assertEqual(score, 1)

    def test_swell_bad(self):
        visitor = PenfoulScoreVisitor(pd.DataFrame())
        bad_swell = Swell(pd.Timestamp.now(), 0.5, 10, 270)
        score = bad_swell.accept(visitor)
        self.assertEqual(score, 0)

    def test_best_session_filtering_good(self):
        mock_df = pd.DataFrame(
            {"hour": ["8:00", "9:00", "10:00"], "score": [1, 1.5, 2]}
        )
        df_filtered = BestSession(mock_df).filtering()
        self.assertEqual(len(df_filtered), 2)

    def test_best_session_filtering_empty(self):
        mock_df = pd.DataFrame(
            {"hour": ["8:00", "9:00", "10:00"], "score": [1, 1.4, 0]}
        )
        df_filtered = BestSession(mock_df).filtering()
        self.assertEqual(len(df_filtered), 0)

    def test_compute_tide_speed_variation(self):
        spot = Spot("Test Vect", 0.0, 0.0)
        spot.add_indicator(Tide(pd.Timestamp("2026-05-30 08:00"), 1.0))
        spot.add_indicator(Tide(pd.Timestamp("2026-05-30 09:00"), 1.5))
        spot.add_indicator(Tide(pd.Timestamp("2026-05-30 10:00"), 1.2))

        spot.compute_tide_speed_vectorial()
        self.assertEqual(spot.marine_indicators["tide"][2].tide_speed, 0.5)
        self.assertAlmostEqual(spot.marine_indicators["tide"][3].tide_speed, -0.3)

    def test_compute_tide_speed_flat(self):
        spot = Spot("Test Flat", 0.0, 0.0)
        spot.add_indicator(Tide(pd.Timestamp("2026-05-30 08:00"), 2.0))
        spot.add_indicator(Tide(pd.Timestamp("2026-05-30 09:00"), 2.0))

        spot.compute_tide_speed_vectorial()
        self.assertEqual(spot.marine_indicators["tide"][2].tide_speed, 0.0)


if __name__ == "__main__":
    unittest.main()
