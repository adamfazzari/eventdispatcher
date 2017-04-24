import json as JSON

from . import DictProperty, ListProperty, Property, StringProperty, EventDispatcher,\
                            ObservableDict, ObservableList
from collections import OrderedDict
from functools import partial
from itertools import chain
import numpy as np


eventdispatcher_map = {dict: DictProperty,        OrderedDict: DictProperty,
                       list: ListProperty,        np.ndarray: ListProperty,
                       tuple: Property,           int: Property,
                       float: Property,           long: Property,
                       bool: Property,            None: Property,
                       unicode: StringProperty,   str: StringProperty}

eventdispatcher_map.update({t: Property for t in (np.int8, np.int16, np.int32, np.int64,
                                                  np.uint8, np.uint16, np.uint32, np.uint64,
                                                  np.float16, np.float32, np.float64,
                                                  )})


class NoAttribute(object):
    pass


class JSON_Map(EventDispatcher):

    def __init__(self, json):
        self.raw = json
        super(JSON_Map, self).__init__(json)

        cls = self.__class__

        # Map the json structure to event dispatcher properties
        # but only those attributes which do not already exist in the object
        properties = JSON_Map.map_attributes(self, json)

        self._python_properties = set()
        for c in cls.__mro__:
            for attr_name, attr in c.__dict__.iteritems():
                if isinstance(attr, property):
                    self._python_properties.add(attr_name)

        self._json_maps = {}
        for attr_name, attr in self.__dict__.iteritems():
            if isinstance(attr, JSON_Map) and attr_name in json:
                self._json_maps[attr_name] = attr

        with self.temp_unbind_all(*self.event_dispatcher_properties.iterkeys()):
            for key in properties.iterkeys():
                if key in json:
                    setattr(self, key, json[key])
        self.bind(**{p: partial(self._update_raw , p) for p in properties})

    def keys(self):
        return [v for v in self.iterkeys()]

    def values(self):
        return [v for v in self.itervalues()]

    def items(self):
        return [v for v in self.iteritems()]

    def get(self, *args):
        return getattr(self, *args)

    def iteritems(self):
        for key in self.iterkeys():
            yield key, getattr(self, key)

    def iterkeys(self):
        return chain(self.event_dispatcher_properties.iterkeys(), self._python_properties, self._json_maps.iterkeys())

    def itervalues(self):
        for key in self.iterkeys():
            yield getattr(self, key)

    def __reduce__(self):
        return dict, tuple(), None, None, self.iteritems()

    def __contains__(self, item):
        return item in self.event_dispatcher_properties or \
               isinstance(getattr(self.__class__, item, AttributeError), property)

    def __getitem__(self, item):
        value = getattr(self, item, KeyError)
        if value is KeyError:
            raise KeyError(item)
        else:
            return value

    def __setitem__(self, key, value):
        if key in self.event_dispatcher_properties or isinstance(getattr(self.__class__, key, AttributeError), property):
            # The key maps to an event dispatcher property or python property
            setattr(self, key, value)
        else:
            raise TypeError('Cannot set %s using item assignment' % key)

    def to_dict(self):
        """
        Creates a dictionary representation of the JSON_Map that includes it's @property values and all sub-JSON_Maps
        """
        d = {}
        for (k, v) in self.iteritems():
            if isinstance(v, JSON_Map):
                d[k] = v.to_dict()
            elif isinstance(v, ObservableDict):
                d[k] = dict(v)
            elif isinstance(v, ObservableList):
                d[k] = list(v)
            else:
                d[k] = v
        return d

    def update(self, E=None, **F):
        if E and self.raw != E:
            for k, v in E.items():
                if hasattr(self[k], 'update'):
                    self[k].update(v)
                else:
                    self[k] = v
        elif F and self.raw != F:
            for k, v in F.items():
                if hasattr(self[k], 'update'):
                    self[k].update(v)
                else:
                    self[k] = v

    def _update_raw(self, property_name, inst, value):
        """
        Callback to keep property values in sync with the underlying JSON object.
        """
        if property_name in self.raw:
            self.raw[property_name] = value
        else:
            raise AttributeError('Attribute %s is not found in the underlying JSON object.' % property_name)

    @staticmethod
    def map_attributes(obj, json):
        """
        Iterate through the JSON structure and create eventdispatcher properties for the attributes
        """
        cls = obj.__class__
        unregistered = {}
        properties = {}
        for attr, value in json.iteritems():
            if hasattr(obj, attr):
                if attr in obj.event_dispatcher_properties:
                    properties[attr] = obj.event_dispatcher_properties[attr]
                continue
            elif any([isinstance(getattr(c, attr, NoAttribute), property) for c in cls.__mro__]):
                # Check if any class attributes are properties
                continue
            else:
                properties[attr] = unregistered[attr] = eventdispatcher_map[type(value)](value)
                setattr(cls, attr, properties[attr])
        if unregistered:
            EventDispatcher.register_properties(obj, unregistered)
        return properties


if __name__ == '__main__':

    path = '/home/local/SENSOFT/clobo/projects/lmx/PygameLMX/resources/platforms/PulseEKKO.conf'
    with open(path, 'r') as f:
        js = JSON.load(f)
    obj = JSON_Map.map('PlatformConfig', js)
    sdfds=3

