from .rule import convert_ruledefs_to_rules, Rule
from .ruledefs import ALL_RULES
import logging

logger = logging.getLogger(__name__)


class Typograph:
    PRESET_NORULES = 0
    PRESET_DEFAULT = 1
    PRESET_ALLRULES = 42

    def __init__(self, preset=None):
        if preset is None:
            preset = self.PRESET_DEFAULT
        logger.info('Loading preset %s' % preset)
        self.rules = self.populate_rules(preset)
        logger.info('%s rules loaded' % len(self.rules))

    def populate_rules(self, preset):
        if preset == self.PRESET_NORULES:
            return []
        s = []
        for ruledef in ALL_RULES:
            s += convert_ruledefs_to_rules(ruledef)
        return s

    def process(self, text):
        for rule in self.rules:
            logger.info('Applying %s' % rule)
            assert isinstance(rule, Rule)
            if rule.disabled:
                continue
            text = rule.apply(text)

            # logger.info('After processing ' + text)
        return text

