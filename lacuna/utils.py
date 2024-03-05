from collections import namedtuple

Result = namedtuple("Result", ["sequence", "score"])

# given a zip of n x m results with dict structure:
# {score: float, token: int, token_str: str, sequence: string}
# return a list of n results with the highest joint score
# using a beam search algorithm
# the function should have the following shape:
# def beam_search(results, k, key):
# where results is a iterable of n iteratable of m results
# k is the beam width
# key is a function that returns the score of a result


def beam_search(
    results, k, key=lambda x: x["score"], mask="[MASK]", adder=lambda x, y: x * y
):
    # initialize the beam with the first set of results
    beam = [
        Result(sequence=result["sequence"], score=key(result)) for result in results[0]
    ]
    # iterate over the remaining sets of results
    for result_set in results[1:]:
        # create a new beam
        new_beam = []
        # iterate over the results in the current set
        for result in result_set:
            # iterate over the results in the current beam
            for partial_result in beam:
                # calculate the score of the current result
                score = key(result)
                # calculate the score of the current beam
                partial_score = partial_result.score
                # calculate the joint score of the current result
                # and the current beam
                joint_score = adder(score, partial_score)
                # append the result to the new beam
                # fill in [MASK] with the token_str
                sequence = partial_result.sequence.replace(mask, result["token_str"])
                new_beam.append(
                    Result(
                        sequence=sequence,
                        score=joint_score,
                    )
                )
        # sort the new beam by score
        new_beam.sort(key=lambda x: x.score, reverse=True)
        # keep the top k results
        beam = new_beam[:k]
    # return the top k results
    return beam


def fill(text, pipe, beam_width=5, top_k=5, mask="[MASK]", adder=lambda x, y: x * y):
    number_of_masks = text.count(mask)
    if number_of_masks == 0:
        return [Result(sequence=text, score=1)]
    results = pipe(
        text,
        top_k=top_k,
    )
    if number_of_masks == 1:
        # return [
        #    Result(sequence=result["sequence"], score=result["score"])
        #    for result in results
        # ]
        return beam_search([results], beam_width, mask=mask, adder=adder)[0:top_k]
    return beam_search(results, beam_width, mask=mask, adder=adder)[0:top_k]


# given a list of tokens, return a list of prompts,
# one for each token, with the token replaced by [MASK]


def create_prompts(tokens, mask="[MASK]"):
    return [" ".join(tokens[:i] + [mask] + tokens[i + 1 :]) for i in range(len(tokens))]
