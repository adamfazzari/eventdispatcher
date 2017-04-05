#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>

#include "eventdispatcher.h"
#include "property.h"
#include "misc.h"

namespace bp = boost::python;


cProperty::cProperty(bp::object obj) {
    //std::cout <<  "call to C++ Property constructor" << std::endl;
    this->default_value = obj;
}

bp::object cProperty::__get__(cEventDispatcher obj, bp::object asd) {
    return obj.event_dispatcher_properties[name]["value"];
    //std::cout <<  "call to C++ __get__: " << value << std::endl;
}

void cProperty::__set__(cEventDispatcher obj, bp::object value) {
    //std::cout <<  "call to C++ __set__: " << value << std::endl;

    if (obj.event_dispatcher_properties[name]["value"] != value) {
        obj.event_dispatcher_properties[name]["value"] = value;
        this->dispatch(obj, value);
    }
}


void cProperty::dispatch(cEventDispatcher obj, bp::object value) {
    //std::cout << "C++ DISPATCHING " << this->name << std::endl;
    bp::object ret;
    bp::object cb;
    // Call all bound callbacks in order. Stop if any bound function returns True
    for (int ii=0; ii < len(obj.event_dispatcher_properties[this->name]["callbacks"]); ii++) {
        cb = bp::extract<bp::object>(obj.event_dispatcher_properties[this->name]["callbacks"][ii]);
        //std::cout << cb << " : ";
        ret = cb(obj, value);

        if (ret  == true) {
            return;
            }
        //std::cout << std::endl;
    };

}

void cProperty::register_property(cEventDispatcher instance, const char* property_name, bp::object default_value) {
    bp::dict info;
    bp::list callback_list;

    this->name = property_name;
    info["property"] = this;
    info["value"] = default_value;
    info["name"] = property_name;
    info["callbacks"] = callback_list;

    this->instances[instance] = info;
    instance.event_dispatcher_properties[property_name] = info;
}

