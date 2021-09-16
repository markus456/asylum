# -*- coding: utf-8 -*-
import os

import pytest
from ndaparser.parser import parseLine, parseStream


def test_parser():
    transactions = []
    with open(os.path.join(os.path.dirname(__file__), "testdata.nda")) as f:
        for line in f:
            transaction = parseLine(line)
            if transaction is not None:
                transactions.append(transaction)
    assert len(transactions) == 12
    assert transactions[2].amount == 40


def test_stream_parser():
    with open(os.path.join(os.path.dirname(__file__), "testdata.nda")) as f:
        transactions = parseStream(f)
        assert len(transactions) == 12
        assert transactions[2].amount == 40
        assert transactions[10].message == "Kulukorvaus remonttitarvikkeista"
