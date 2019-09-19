"""Necromancer DoT Simulator."""
import argparse
import logging
import sys


class Spell:
    """Spell object.

    :param dict attrs: key/value pairs for attributes of the spell.
    """

    def __init__(self, attrs):
        """Default class constructor."""
        name = attrs.get('name')
        min_level = attrs.get('min_level')
        max_level = attrs.get('max_level')
        min_dmg = attrs.get('min_dmg')
        max_dmg = attrs.get('max_dmg')
        cast_time = attrs.get('cast_time')
        refresh_time = attrs.get('refresh_time')
        mana_cost = attrs.get('mana_cost')
        duration = attrs.get('duration')


class Character:
    """Character object.

    :param dict attrs: key/value pairs for attributes of the character."""

    def __init__(self, attrs):
        duration_level = attrs.get('duration_level')
        duration_value = attrs.get('duration_value')
        pres_level = attrs.get('pres_level')
        pres_min_value = attrs.get('min_pres_level')
        pres_max_value = attrs.get('max_pres_level')
        haste_level = attrs.get('haste_level')
        haste_value = attrs.get('haste_value')
        poison_level = attrs.get('poison_level')
        disease_level = attrs.get('disease_level')
        corrupt_level = attrs.get('corrupt_level')
        magic_level = attrs.get('magic_level')
        fire_level = attrs.get('fire_level')
        poison_min_value = attrs.get('poison_min_value')
        poison_max_value = attrs.get('poison_max_value')
        disease_min_value = attrs.get('disease_min_value')
        disease_max_value = attrs.get('disease_max_value')
        corrupt_min_value = attrs.get('corrupt_min_value')
        corrupt_max_value = attrs.get('corrupt_max_value')
        magic_min_value = attrs.get('magic_min_value')
        magic_max_value = attrs.get('magic_max_value')
        epic_2_0 = attrs.get('epic_2_0')
        epic_2_5 = attrs.get('epic_2_5')


class Simulation:
    """Simulation object"""

    def __init__(self):
        self.applied_dots = []
        self.dot_list = []
        self.damage = 0
        self.mana = 0
        self.display_time = None

    def check_current_dots(self, cur_time):
        """Check the applied dots and see if they will wear off at this time."""
        new_dots = []
        for entry in self.applied_dots:
            if cur_time >= entry['wear_off']:
                continue
            new_dots.append(entry)
        self.applied_dots = new_dots

    def calc_damage(self):
        """Iterate through the applied dots and add their damage."""
        for entry in self.applied_dots:
            # TODO: Create damage_handler()
            pass

    def cast_dot(self, display_time):
        """Cast the next best dot that isn't currently applied."""
        # Dots are always put in the order that they deal the highest absolute damage/time
        to_apply = None
        for dot in self.dot_list:
            # See if the dot is already applied.  If it is, skip to the next.
            applied = False
            for entry in self.applied_dots:
                if dot['name'] == entry['name']:
                    applied = True
                    break
            if applied:
                continue

            # Apply the dot
            to_apply = dot
            break

        if to_apply:
            return to_apply['cast'], (to_apply ['cast'] + to_apply['refresh']), to_apply
        else:
            return 0, 0, None

    def add_dot(self, dot, cur_time):
        """Add the dot to the dot list."""
        dot.update({'wear_off': cur_time + dot['duration']})
        self.applied_dots.append(dot)
        self.mana += dot['mana']

    def simulate(self, timeframe):
        """Simulates combat."""
        cur_time = 0
        cast_end = 0
        refresh_end = 150
        dot = self.dot_list[0]

        while cur_time < timeframe:
            self.display_time = int(cur_time / 100)

            # Server ticks are every six seconds (600)
            if cur_time > 0 and cur_time % 600 == 0:
                # Calculate damage from all current dots
                self.calc_damage()

            # Check all applied dots and see if any of them will wear off here.
            self.check_current_dots(cur_time)

            # Is the current time greater than our cast time, but less than the refresh time?
            if cast_end <= cur_time <= refresh_end:
                self.add_dot(dot, cur_time)

                # Setting cast_end to the timeframe prevents this from being called over and over
                cast_end = timeframe
            elif cur_time >= refresh_end and len(self.applied_dots) != len(self.dot_list):
                # Cast the next dot

                cast, refresh, dot = self.cast_dot()
                cast_end = cur_time + cast
                refresh_end = cur_time + refresh

            # Move to the next hundredth of a second
            cur_time += 1


if __name__ == '__main__':
    # Configure logging
    log = logging.getLogger('simulation_log')
    formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s', '%m/%d/%Y-%I%M%S %p')
    handler = logging.FileHandler('simulation.log')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.info('EverQuest Necromancer DoT Simulator: ')

    # Parse Arguments to configure how to proceed
    parser = argparse.ArgumentParser()

    # Add the "level" argument
    __help = ("Specify the game era.  If not specified, 'The Burning Lands' will be used.  Use commonly "
              "accepted abbreviations, such as RoK for Kunark or TBL for The Burning Lands.")
    parser.add_argument('-e', '--era', action='store', type=str, help=__help)

    # Add the "baseline" argument
    __help = ('Set this flag to use baseline (no focuses, rank 1 spells only, no AAs).  Mutually '
              'exclusive with the -g / --group and -r / --raid flags.')
    parser.add_argument('-b', '--baseline', action='store_true', help=__help)

    # Add the "group" argument
    __help = ('Set this flag to use group settings (group focuses, rank 2 spells, all previous era AAs).'
              ' Mutually exclusive with the -b / --baseline and -r / --raid flags.')
    parser.add_argument('-g', '--group', action='store_true', help=__help)

    # Add the "raid" argument
    __help = ('Set this flag to use raid settings (raid focuses, rank 3 spells, all current era AAs). '
              'Mutually exclusive with the -b / --baseline and -g / --group flags.  This is the default '
              'option.')
    parser.add_argument('-r', '--raid', action='store_true', help=__help)

    # Add the "yaml" argument
    __help = 'REQUIRED: Specify the file path to a .yaml file containing spell settings.'
    parser.add_argument('-s', '--spells', action='store', type=str, help=__help)

    # Add the "timescale" argument
    __help = ('Specify the number of hours to simulate.  By default, this will be set to 48 hours.  It '
              'is recommended that simulations be at least 24 hours to prevent burst damage from '
              'affecting the parse.')
    parser.add_argument('-t', '--timescale', action='store', type=int, help=__help)

    # Add the "epic 2.0" argument
    __help = ('Set this flag to set if the necromancer has their epic 2.0.  For expansions prior to '
              'omens of war, this option is ignored.  By default, this assumed to be True.')
    parser.add_argument('--epic_two', action='store_true', help=__help)

    # Add the "epic 2.5" argument
    __help = ('Set this flag to set if the necromancer has the epic 2.5 augment.  For expansions prior '
              'to depths of darkhollow, this option is ignored.  By default, this is assumed to be '
              'True if the necromancer has their 2.0, False otherwise.')
    parser.add_argument('--epic_two_five', action='store_true', help=__help)

    args = parser.parse_args()

    # Validate era
    if not args.era:
        log.error('Era automatically set to "TBL"')
        era = "tbl"
    else:
        valid_era_list = ['classic', 'rok', 'sov', 'sol', 'pop', 'loy', 'ldon', 'god', 'oow', 'don',
                          'dodh', 'por', 'tss', 'tbs', 'sof', 'sod', 'uf', 'hot', 'voa', 'rof', 'cotf',
                          'tds', 'tbm', 'eok', 'ros', 'tbl']
        if args.era.lower() not in valid_era_list:
            log.error(f'Supplied era "{args.era}" is not a valid era.')
            log.info(f'Valid era entries are: "{valid_era_list}".')
            sys.exit(1)
        else:
            era = args.era.lower()

    # Validate baseline, group, and raid


    # Configure the Character object
    # Configure a number of Spell objects with castable spells
    # Add the spells to the simulation
    # Begin the simulation
    # Report the results
