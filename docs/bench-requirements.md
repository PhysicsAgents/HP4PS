# Bench Sample Requirements

English | [中文](bench-requirements.zh.md)

> The Chinese version is the original. This is a translation; where they differ, the Chinese version governs.

This document describes the basic requirements for building bench samples from a curated set of papers.

1. Samples verified in QA form are forbidden. Verification conditions must be built on a solution that the agent outputs by following some protocol standard, such as a code standard (Python, C, Lean 4, and so on).
2. Every sample must have a standard solution, namely the solution reproduced from the corresponding paper.
3. Every sample must make it possible to exceed the upper limit of the solution proposed in the corresponding paper. That is, the test environment and test content must not simply reproduce the paper; instead, a unified test environment should be built for the corresponding broad category, and the conditions in each paper can be formalized as configuration or special patches. Aim for traceability upward and backward, not just the present.
4. When constructing the standard protocol, first consider whether an existing solution or partial solution exists. When self-implemented content exceeds 30% of the whole, consider giving up or contacting the administrator.
