#!/usr/bin/env python
#
# Optimize blocksize of apps/mmm_block.cpp
#
# This is an extremely simplified version meant only for tutorials
#
import adddeps  # fix sys.path
import argparse
import sys
import random
from pprint import pprint

import opentuner
from opentuner.search import manipulator
from opentuner import MeasurementInterface
from opentuner import Result

argparser = argparse.ArgumentParser(parents=opentuner.argparsers())
argparser.add_argument(
  '--num-params', type=int, default=300, help='number of parameters to use')
argparser.add_argument(
  '--show-diffs', default=False, action='store_true', help='show changes at each generation')
argparser.add_argument(
  '--use-enum-param', default=False, action='store_true', help='use enum instead of boolean param')
argparser.add_argument(
  '--use-int-param', default=False, action='store_true', help='use Integer instead of boolean param')

class ConvTestTuner(opentuner.measurement.MeasurementInterface):

  def __init__(self, *pargs, **kwargs):
    super(ConvTestTuner, self).__init__(program_name='test', *pargs, **kwargs)
    self.args = args
    print args
    self.goals={}
    self.testnum = 0
    self.prevcfg = None
    
  def manipulator(self):
    """
    Define the search space by creating a
    ConfigurationManipulator
    """
    m = manipulator.ConfigurationManipulator()
    self.goals={}
    self.trace = {}
    self.weight = {}
    weightTotal = 0
    for n in range(self.args.num_params):
      pname = 'P%03d' % (n)
      randbool = random.randint(0,1) == 0
      if self.args.use_enum_param:
        m.add_parameter(manipulator.EnumParameter(pname, ['on', 'off']))
        self.goals[pname] = 'off' if randbool else 'on'
      elif self.args.use_int_param:
        m.add_parameter(manipulator.IntegerParameter(pname, 256, 257))
        self.goals[pname] = 256 if randbool else 257
      elif self.args.use_logint_param:
        m.add_parameter(manipulator.LogIntegerParameter(pname, 256, 257))
        self.goals[pname] = 256 if randbool else 257
      else:
        m.add_parameter(manipulator.BooleanParameter(pname))
        self.goals[pname] = randbool 
      self.trace[pname] = {}
      weight = n*n + 1
      self.weight[pname] = weight
      weightTotal += weight
      
    self.maxscore = weightTotal + 1
    self.best = self.maxscore
    self.bestcfg = None
    if False:
      print 'goals = ',
      pprint(self.goals)
    
    return m

  def run(self, desired_result, input, limit):
    self.testnum += 1
    cfg = desired_result.configuration.data
    # self.call_program('true')
    score = self.maxscore
    nonMatches = 0
    lastNonMatch = None
    for p in sorted(cfg.keys()):
      # mark in trace
      self.trace[p][cfg[p]] = 1
      if cfg[p] == self.goals[p]:
        score -= self.weight[p]
      else:
        nonMatches += 1
        lastNonMatch = p
    if self.args.show_diffs and self.prevcfg is not None:
      print '%d:' % (self.testnum),
      for p in sorted(cfg.keys()):
        if cfg[p] != self.prevcfg[p]:
          print p,
      print

       
        
    if score < self.best:
      self.best = score
      print 'score=%d, (%d wrong) after %d tests' % (score, nonMatches, self.testnum),
      if lastNonMatch is not None:
        print ', highest=%s, weight %d' % (lastNonMatch, self.weight[lastNonMatch]),
      if False and self.bestcfg is not None:
        print ', changes:',
        for p in sorted(cfg.keys()):
          if cfg[p] != self.bestcfg[p]:
            print '%s,' % p,
      print

      self.bestcfg = cfg
      if lastNonMatch is None:
        print 'reached perfect score, exiting'
        sys.exit(0)

    self.prevcfg = cfg
    return Result(time=score)

  
  def save_final_config(self, finalCfg):
    """called at the end of tuning"""
    if True:
      cfgDict = self.bestcfg
    else:
      cfgDict = finalCfg.data
    print 'best score was %d, discrepancies follow:' % self.best
    for p in sorted(cfgDict.keys()):
      if cfgDict[p] != self.goals[p]:
        print '(%s, weight %d)  ' % (p, self.weight[p]),
    

  
if __name__ == '__main__':
  args = argparser.parse_args()
  ConvTestTuner.main(args)
