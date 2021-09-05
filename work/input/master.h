////////////////////////////////////////////////////////////////////////////////
// Copyright (c) 2017-2018 Clemson University.
//
// This file was originally written by Bradley S. Meyer.
//
// This is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
//
// This software is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this software; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
// USA
//
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
//!
//! \file master.hpp
//! \brief A file to include all helper routines.
//!
////////////////////////////////////////////////////////////////////////////////

#include "network_data/detail/default.hpp"
#include "network_data/network_data.hpp"

#include "zone_data/single_zone/detail/default.hpp"
#include "zone_data/single_zone/zone_data.hpp"

#include "properties_updater/detail/record_initial_t9_rho.hpp"
#include "properties_updater/properties_updater.hpp"

#include "outputter/detail/xml_text_writer.hpp"
#include "outputter/outputter.hpp"

#include "nse_corrector/detail/default.hpp"
#include "nse_corrector/nse_corrector.hpp"

#include "screener/detail/default.hpp"
#include "screener/screener.hpp"

#include "thermo/detail/default.hpp"
#include "thermo/thermo.hpp"

#include "network_evolver/single_zone/detail/default.hpp"
#include "network_evolver/single_zone/network_evolver.hpp"

#include "network_limiter/detail/default.hpp"
#include "network_limiter/network_limiter.hpp"

#include "hydro/single_zone/standard/detail/default.hpp"
#include "hydro/single_zone/standard/hydro.hpp"

#include "time_adjuster/detail/default.hpp"
#include "time_adjuster/time_adjuster.hpp"

#include "matrix_modifier/detail/specific_species.hpp"
#include "matrix_modifier/matrix_modifier.hpp"

#include "network_time/detail/default.hpp"
#include "network_time/network_time.hpp"

#include "rate_modifier/detail/default.hpp"
#include "rate_modifier/rate_modifier.hpp"

#include "rate_registerer/detail/aa522a25.hpp"
#include "rate_registerer/rate_registerer.hpp"

#include "step_printer/detail/default.hpp"
#include "step_printer/step_printer.hpp"

#include "inputter/inputter.hpp"
