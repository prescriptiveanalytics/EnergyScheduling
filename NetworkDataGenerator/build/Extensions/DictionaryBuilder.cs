namespace Build.Extensions;

public sealed class DictionaryBuilder<TKey, TValue> where TKey : notnull
{
	private readonly ImmutableDictionary<TKey, TValue>.Builder builder = ImmutableDictionary.CreateBuilder<TKey, TValue>();

	public DictionaryBuilder<TKey, TValue> Add(TKey key, TValue value)
	{
		builder.Add(key, value);
		return this;
	}

	public DictionaryBuilder<TKey, TValue> Remove(TKey key)
	{
		builder.Remove(key);
		return this;
	}

	public ImmutableDictionary<TKey, TValue> Build() => builder.ToImmutable();
}
