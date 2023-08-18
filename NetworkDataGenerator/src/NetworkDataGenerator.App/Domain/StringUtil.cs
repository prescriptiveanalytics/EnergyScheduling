// Copyright (C) 2018-present RISC Software GmbH <office@risc-software.at>.
// This file is part of the RISC Ibex framework.
// This code must not be copied and/or used without permission of RISC Software GmbH.

using System;

namespace NetworkDataGenerator.App.Domain
{
    public sealed class StringUtil
    {
        // https://stackoverflow.com/questions/2749662/string-comparison-invariantcultureignorecase-vs-ordinalignorecase
        // https://stackoverflow.com/questions/72696/which-is-generally-best-to-use-stringcomparison-ordinalignorecase-or-stringco
        // "Also, please keep in mind that OrdinalIgnoreCase is a very special kind of beast, that is picking and choosing a bit of an ordinal compare with some mixed in lexicographic aspects. This can be confusing."
        public const StringComparison ComparisonIgnoreCase = StringComparison.InvariantCultureIgnoreCase;
    }
}
