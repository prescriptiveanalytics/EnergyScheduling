// Copyright (C) 2018-present RISC Software GmbH <office@risc-software.at>.
// This file is part of the RISC Ibex framework.
// This code must not be copied and/or used without permission of RISC Software GmbH.

using System;

namespace NetworkDataGenerator.App.Domain
{
    public class EncoderException : Exception
    {
        public EncoderException()
        {
        }

        public EncoderException(string message)
            : base(message)
        {
        }

        public EncoderException(string message, Exception inner)
            : base(message, inner)
        {
        }
    }
}
