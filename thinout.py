
from datetime import date, timedelta
import os.path, types


class Timeline(dict):
   def first(self):
      ks = self.keys()
      ks.sort()
      return ks[0] if ks else None
   def last(self):
      ks = self.keys()
      ks.sort()
      return ks[-1] if ks else None

   def serialize(self, begin=None, end=None, empty=' '):
      if begin is None:
         begin = self.first()
      if end is None:
         end = self.last()

      if begin is None:
         return ''

      s = ''
      pos = begin
      while pos < end:
         if pos in self:
            s += self[pos]
         else:
            s += empty
         pos = pos + timedelta(days=1)
      return s


class Item(object):
   def __init__(self, date):
      self.date = date
   def weight(self, context, index):
      return 1.0


class Bucket(object):
   def __init__(self, begin, end, capacity):
      if begin > end:
         raise ValueError("begin > end")
      self.begindate = begin
      self.enddate = end
      self.capacity = capacity
      self.beginidx = None
      self.endidx = None

   def too_many(self):
      '''Check if there are too many items in the bucket'''
      return (self.endidx - self.beginidx) > self.capacity

   def find_rmitem(self, items):
      '''find item to remove in [begin:end['''
      begin = self.beginidx
      end = self.endidx
      if begin >= end:
         # no items
         raise Exception("empty interval")
      if begin+1 == end:
         # one item
         return begin
      if end == len(items):
         # keep globally newest item
         end -= 1
      if begin+1 == end:
         # one item remaining
         return begin
      if begin == 0:
         # keep globally oldest item
         begin += 1

      # check items
      rmweight = None
      rm = None
      for i in range(begin, end):
         hole = items[i+1].date - items[i-1].date
         weight = items[i].weight(items, i) * 1.0 / hole.days
         #print "%s: adj. del priority %f" % (items[i].date, weight)
         if (rmweight is None) or (weight > rmweight):
            rmweight = weight
            rm = i
      return rm

   def print_state(self):
      print "%s - %s (%d/%d)" % (self.begindate, self.enddate, self.endidx - self.beginidx, self.capacity)


class Thinout(object):
   def __init__(self, intervalls, items, enddate=None):
      self.items = list(sorted(items, key=(lambda it: it.date)))
      if enddate is None:
         enddate = date.today() + timedelta(days=1)
      self.enddate = enddate
      self._make_buckets(intervalls)
      self.removed = []

   def _make_buckets(self, intervalls):
      buckets = []

      offset = 0
      end = self.enddate
      for (span, count) in intervalls:
         if span < count:
            raise Exception("cannot keep %d items in %d days" % (count, span))
         begin = end - timedelta(days=span)
         buckets.append(Bucket(begin, end, count))
         end = begin
      self.buckets = list(reversed(buckets))
      self._set_bucket_indexes()

   def _set_bucket_indexes(self):
      idx = 0
      for bucket in self.buckets:
         while idx < len(self.items) and self.items[idx].date < bucket.begindate:
            idx += 1
         bucket.beginidx = idx
         while idx < len(self.items) and self.items[idx].date < bucket.enddate:
            idx += 1
         bucket.endidx = idx

   def _extract_rm_item(self):
      for bucket in self.buckets:
         if bucket.too_many():
            rmidx = bucket.find_rmitem(self.items)
            rm = self.items[rmidx]
            del self.items[rmidx]
            self._set_bucket_indexes()
            return rm
      return None

   def extract_rm_items(self):
      while 1:
         rm = self._extract_rm_item()
         if rm is None:
            return
         else:
            self.removed.append(rm)
            yield rm

   def items_timeline(self):
      tl = Timeline()
      for item in self.removed:
         tl[item.date] = '.'
      for item in self.items:
         tl[item.date] = 'x'
      return tl

   def buckets_timeline(self):
      tl = Timeline()
      for b in self.buckets:
         tl[b.begindate] = '['
         tl[b.enddate] = '['

         # add labels
         span = b.enddate.toordinal() - b.begindate.toordinal() - 1
         scap = str(b.capacity)
         lcap = len(scap)
         if span >= lcap:
            ofs = (span-lcap) / 2
            for i in range(lcap):
               tl[b.begindate + timedelta(days=ofs+i+1)] = scap[i]
      return tl

   def print_overview(self):
      itl = self.items_timeline()
      btl = self.buckets_timeline()
      print itl.serialize(end=self.enddate)
      print btl.serialize(begin=itl.first(), end=self.enddate+timedelta(days=1))
      return
      endofs = self.buckets[-1].enddate.toordinal() - self.items[-1].date.toordinal()
      if endofs > 0:
         # buckets later than items
         itl += ' ' * endofs
      if endofs < 0:
         # later items than buckets
         btl += '.' * (-endofs)

      lim = len(itl)
      if lim > len(btl):
         btl = '.' * (lim - len(btl)) + btl

      print itl
      print btl[-lim:]
      print

   def print_weights(self):
      print "weights:"
      for i, item in enumerate(self.items):
         print "  %s: %s" % (item.date, item.weight(self.items, i))


def testseries():
   intervalls = [
         (4, 4),
         (15, 5),
         (40, 4),
      ]

   today = date.today()
   items = []

   mitems = 80
   for i in range(mitems):
      nd = today + timedelta(days=i)
      items.append(Item(nd))

      th = Thinout(intervalls, items, nd+timedelta(days=1))
      for it in th.extract_rm_items():
         pass
      print_overview(th)

   print "====="

   mitems = 80
   items = []
   for i in range(mitems):
      nd = today + timedelta(days=i)
      items.append(Item(nd, 0))

      th = Thinout(intervalls, items, nd+timedelta(days=1))
      for it in th.extract_rm_items():
         items.remove(it)
      print_overview(th)


   #t = ''
   #b = ''
   #for i in range(mitems):
   #   t += '%d' % (i%10)
   #   if i%10:
   #      b += ' '
   #   else:
   #      b += '%d' % (i/10)
   #print t
   #print b

   print "reamining:", len(items)


class FileItem(Item):
   def __init__(self, path):
      Item.__init__(self, date.fromtimestamp(os.path.getmtime(path)))
      self.path = path


if __name__ == '__main__':
   testseries()

