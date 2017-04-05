#ifndef MISC_INCLUDED

#define MISC_INCLUDED

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>


namespace bp = boost::python;


// Define an operator that works on boost::python::object
std::ostream& operator<<(std::ostream& os, const bp::object& o);


#endif // MISC_INCLUDED
