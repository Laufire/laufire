r"""
YamlEx
======

A wrapper around HiYaPyCo that supports:

* Easier file handling.
* Runtime variables.

#Later: Allow external template sources. ie: The source data won't be in the rendered data. This passibly could be a KWArg named, env.
"""
from hiyapyco import HiYaPyCo, dump, odyldo
from jinja2 import Template

from .extensions import merge

# #Later: Make YamlEx to inherit 'dict', so that it could support all the functionalities of a dict.
class YamlEx:
	r"""The wrapper class.

	Args:
		*FilePaths: A list of YAML files to load.
	"""
	def __init__(self, *FilePaths, **KWArgs):
		if FilePaths and FilePaths[0] is None: # None is supplied for the file path.
			FilePaths = None

		self.HiYaPyCo = H = HiYaPyCo(*FilePaths, **KWArgs) if FilePaths else HiYaPyCo('---\n{}', **KWArgs) # return an empty object when no file is mentioned.
		self.Data = H._data #pylint: disable=W0212

	def __get_item__(self, key):
		return self.Data[key]

	def setData(self, Data):
		r"""Explicitly sets self.Data.

		Note:
			An explicit set method is used instead of getters and setters, as the way to implement them in this context coudn't be found (@property + new style classes, meddles with __getitem__).
		"""
		self.Data = Data
		self.HiYaPyCo._data = Data #pylint: disable=W0212

		return self

	def extend(self, DataToMerge):
		r"""
		Extends the existing data by merging it with the given data.
		"""
		from laufire.extensions import merge

		Data = merge(self.Data, DataToMerge)
		self.Data = Data
		self.HiYaPyCo._data = Data #pylint: disable=W0212

		return self

	def interpolate(self):
		r"""Does the interpolation.
		"""
		self.HiYaPyCo._interpolate(self.Data) #pylint: disable=W0212
		return self

	def load(self, filePath, interpolate=True):
		r"""Loads data from the given YAML file.

		Args:
			filePath (str): A path to a valid YAML file.
		"""
		self.setData(merge(self.Data, odyldo.safe_load(open(filePath, 'r'))))

		if interpolate:
			self.interpolate()

		return self

	def dump(self, defaultFlowStyle=True):
		r"""Returns the YAML dump.
		"""
		return dump(self.Data, defaultFlowStyle)

	def render(self, tmplStr):
		r"""Renders the given template.
		"""
		return Template(tmplStr).render(self.Data)

	# Allow access to the underlying dictionary attrs, this also will allow access to the keys of self.Data.
	def __getattr__(self, attr):
		return getattr(self.Data, attr)

def overlayHiYaPyCo():
	import hiyapyco
	from jinja2 import Environment, Undefined
	from jinja2.utils import missing
	from jinja2._compat import implements_to_string

	# Allow the undefined vars to be as is
	@implements_to_string
	class UntouchedUndefined(Undefined):
		r"""Skips the undefined variables during interpolation, to allow runtime variable assignments.
		"""
		__slots__ = ()

		def __str__(self):
			if self._undefined_obj is missing:
				return u'{{ %s }}' % self._undefined_name

			return self

		__iter__ = __len__ = __nonzero__ = __eq__ = __ne__ = __bool__ = __hash__ = __str__

	hiyapyco.jinja2env = Environment(undefined=UntouchedUndefined)

	# Hook into HiYaPyCo._interpolatestr so that string could be interpolated recursively.

	HiYaPyCo._interpolatestr_orig = HiYaPyCo._interpolatestr #pylint: disable=W0212

	def _interpolatestrHook(self, s):
		rendered = self._interpolatestr_orig(s) #pylint: disable=W0212

		while s != rendered:
			s = rendered
			rendered = self._interpolatestr_orig(s) #pylint: disable=W0212

		return s

	HiYaPyCo._interpolatestr = _interpolatestrHook #pylint: disable=W0212

if not hasattr(HiYaPyCo, '_interpolatestr_orig'): # Skip overlaying, if the module is parsed more than one time (through import collision etc).
	overlayHiYaPyCo()
