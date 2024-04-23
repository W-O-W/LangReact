from langreact.core.builder.output_builder import *


def test_default_output_builder():
    output_builder = DefaultOutputBuilder("GPT")

    chunks = [
        Chunk(data="请问今天天气如何"),
        Chunk(data="北京"),
        Chunk(data="北京今日晴天"),
        Chunk(
            data="根据天气查询的结果为[SEP]北京今日晴天[SEP]请问今天天气如何?",
        ),
        Chunk(command="GPT", data="今天晴天,"),
        Chunk(command="GPT", data="很适合出门."),
    ]
    for chunk in chunks[:4]:
        assert output_builder.match_and_append(chunk) == False

    for chunk in chunks[4:]:
        assert output_builder.match_and_append(chunk)

    assert len(output_builder.chunks) == 2
    assert output_builder.build() == Chunk(command="GPT", data="很适合出门.")
