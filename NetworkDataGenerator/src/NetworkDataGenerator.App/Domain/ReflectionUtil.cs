// Copyright (C) 2018-present RISC Software GmbH <office@risc-software.at>.
// This file is part of the RISC Ibex framework.
// This code must not be copied and/or used without permission of RISC Software GmbH.

using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;

namespace NetworkDataGenerator.App.Domain
{
    public sealed class ReflectionUtil
    {
        //private static readonly Logger s_logger = LogManager.GetCurrentClassLogger();

        /// <summary>
        /// Returns the value of the given property
        /// as a formatted string, depending on its type.
        /// </summary>
        /// <param name="property">The property to get the value string of.</param>
        /// <returns>The property's value as a formatted string.</returns>
        public static string GetPropertyValueString(object property)
        {
            Type propType = property.GetType();

            if (IsTupleType(propType, true))
            {
                IEnumerable<object> propList = GetValuesFromTuple(property as ITuple);
                if (propList == null) return "";

                string propertyListValues = "<";
                int i = 0;
                foreach (object val in propList)
                {
                    propertyListValues += (i++ > 0 ? ", " : "") + GetPropertyValueString(val);
                }
                propertyListValues += ">";
                return propertyListValues;
            }

            if (propType.IsArray || property is IList && propType.IsGenericType)
            {
                if (property is not IList propList) return "";

                string propertyListValues = "{";
                for (int i = 0; i < propList.Count; ++i)
                {
                    object val = propList[i];
                    propertyListValues += (i > 0 ? ", " : "") + GetPropertyValueString(val);
                }
                propertyListValues += "}";
                return propertyListValues;
            }

            if (propType.IsClass && !propType.IsValueType)
            {
                return propType.Name;// GetFriendlyName();
            }

            return property.ToString();
        }

        /// <summary>
        /// Returns the tuple values as an enumerable of objects.
        /// </summary>
        /// <param name="tuple">The tuple to enumerate the values of.</param>
        /// <returns>An enumerable of the given tuple's values</returns>
        public static IEnumerable<object> GetValuesFromTuple(ITuple tuple)
        {
            for (int i = 0; i < tuple.Length; i++)
                yield return tuple[i];
        }

        /// <summary>
        /// Determines whether the given type is a Tuple type.
        /// https://stackoverflow.com/a/28772413
        /// </summary>
        /// <param name="type">The type to evaluate.</param>
        /// <param name="checkBaseTypes">Indicates whether the base types should be evaluated.</param>
        /// <returns>True if the given type is a tuple type.</returns>
        public static bool IsTupleType(Type type, bool checkBaseTypes = false)
        {
            if (type == null)
                throw new ArgumentNullException(nameof(type));

            if (type == typeof(Tuple))
                return true;

            while (type != null)
            {
                if (type.IsGenericType)
                {
                    Type genType = type.GetGenericTypeDefinition();
                    if (genType == typeof(Tuple<>)
                        || genType == typeof(Tuple<,>)
                        || genType == typeof(Tuple<,,>)
                        || genType == typeof(Tuple<,,,>)
                        || genType == typeof(Tuple<,,,,>)
                        || genType == typeof(Tuple<,,,,,>)
                        || genType == typeof(Tuple<,,,,,,>)
                        || genType == typeof(Tuple<,,,,,,,>)
                        || genType == typeof(Tuple<,,,,,,,>))
                        return true;
                }

                if (!checkBaseTypes)
                    break;

                type = type.BaseType;
            }

            return false;
        }

        /// <summary>
        /// Checks whether the given object has a null or a default value.
        /// https://stackoverflow.com/a/6553276
        /// </summary>
        /// <typeparam name="T">The type of the object.</typeparam>
        /// <param name="argument">The object to evaluate.</param>
        /// <returns>True if the given object has a null or default value.</returns>
        public static bool IsNullOrDefault<T>(T argument)
        {
            // deal with normal scenarios
            if (argument == null) return true;
            if (Equals(argument, default(T))) return true;

            // deal with non-null nullables
            Type methodType = typeof(T);
            if (Nullable.GetUnderlyingType(methodType) != null) return false;

            // deal with boxed value types
            Type argumentType = argument.GetType();
            if (argumentType.IsValueType && argumentType != methodType)
            {
                object obj = Activator.CreateInstance(argument.GetType());
                return obj.Equals(argument);
            }

            return false;
        }

        /// <summary>
        /// Creates instances of the given types.
        /// This assumes that the given types have a common base type, as well as default constructors!
        /// </summary>
        /// <typeparam name="T">The base type of the given types.</typeparam>
        /// <param name="types">The list of types to generate instances of.</param>
        /// <returns>A list of instances.</returns>
        public static IList<T> CreateInstances<T>(IList<Type> types)
        {
            return CreateInstances<T>(types, new List<object[]> { Array.Empty<object>() });
        }

        /// <summary>
        /// Creates instances of the given types.
        /// This assumes that the given types have a common base type, as well as constructors with the same signature!
        /// </summary>
        /// <typeparam name="T">The base type of the given types.</typeparam>
        /// <param name="types">The list of types to generate instances of.</param>
        /// <param name="constructorArgs">The arguments to generate the instances with (constructor arguments).</param>
        /// <returns>A list of instances.</returns>
        public static IList<T> CreateInstances<T>(IList<Type> types, List<object[]> constructorArgs)
        {
            List<T> instances = new();
            foreach (Type t in types)
            {
                object instance = null;
                foreach (object[] args in constructorArgs)
                {
                    Type[] constructorTypes = new Type[args.Length];
                    for (int i = 0; i < args.Length; ++i)
                    {
                        constructorTypes[i] = args[i].GetType();
                    }
                    if (t.GetConstructor(BindingFlags.Instance | BindingFlags.Public, null, CallingConventions.HasThis, constructorTypes, null) != null)
                    {
                        instance = Activator.CreateInstance(t, args);
                        break;
                    }
                }
                if (instance != null)
                    instances.Add((T)instance);
                //else
                //    s_logger.Error($"Could not create instance of {t.Name}. Did not find appropriate constructor.");
            }

            return instances;
        }

        /// <summary>
        /// Creates an instance of the given type.
        /// </summary>
        /// <param name="type">The type to generate an instance of.</param>
        /// <param name="args">The constructor arguments.</param>
        /// <returns>An instance of the given type as an object.</returns>
        public static object CreateInstance(Type type, object[] args)
        {
            return Activator.CreateInstance(type, args);
        }

        /// <summary>
        /// Creates an instance of the given type.
        /// </summary>
        /// <typeparam name="T">The base type to cast the instance to.</typeparam>
        /// <param name="type">The type to generate an instance of.</param>
        /// <param name="args">The constructor arguments.</param>
        /// <returns>An instance of the given type, cast to its base type.</returns>
        public static T CreateInstance<T>(Type type, object[] args)
        {
            object instance = Activator.CreateInstance(type, args);
            return (T)instance;
        }

        /// <summary>
        /// Returns a list of types implementing the given interface in the currently loaded assemblies.
        /// </summary>
        /// <param name="interfaceType">The interface to look for.</param>
        /// <returns>A list of types implementing the given interface.</returns>
        public static List<Type> GetAllTypesImplementingInterface(Type interfaceType)
        {
            return GetAllTypesImplementingInterface(interfaceType, AppDomain.CurrentDomain.GetAssemblies());
        }


        /// <summary>
        /// Lists all IBEX assemblies in the given directory.
        /// </summary>
        /// <param name="path">The directory to search.</param>
        /// <returns>The array of IBEX assemblies.</returns>
        [System.Diagnostics.CodeAnalysis.SuppressMessage("Design", "CA1031:Keine allgemeinen Ausnahmetypen abfangen", Justification = "<Ausstehend>")]
        public static Assembly[] GetIbexAssembliesInDirectory(string path)
        {
            List<Assembly> allAssemblies = new();
            string[] dlls = Directory.GetFiles(path, "riscsw.ibex.*.dll");
            foreach (string dll in dlls)
            {
                try
                {
                    allAssemblies.Add(Assembly.LoadFrom(dll));
                }
                catch (Exception)
                {
                    //s_logger.Warn($"Could not load assembly {dll}.");
                }
            }
            return allAssemblies.ToArray();
        }

        /// <summary>
        /// Returns a list of types implementing the given interface in IBEX assemblies found in the current execution directory.
        /// </summary>
        /// <param name="interfaceType">The interface to look for.</param>
        /// <returns>A list of types implementing the given interface.</returns>
        public static List<Type> GetAllTypesImplementingInterfaceInIbexAssemblies(Type interfaceType)
        {
            string path = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            return GetAllTypesImplementingInterface(interfaceType, GetIbexAssembliesInDirectory(path));
        }

        /// <summary>
        /// Returns a list of types implementing the given interface in the given assemblies.
        /// </summary>
        /// <param name="interfaceType">The interface to look for.</param>
        /// <param name="assemblies">The assemblies to search.</param>
        /// <returns>A list of types implementing the given interface.</returns>
        private static List<Type> GetAllTypesImplementingInterface(Type interfaceType, Assembly[] assemblies)
        {
            return assemblies.SelectMany(s => GetLoadableTypes(s))
                .Where(p => interfaceType.IsAssignableFrom(p) && !p.IsInterface && !p.IsAbstract).ToList();
        }

        /// <summary>
        /// Only fetch loadable types from the given assembly.
        /// See answer by Jon Skeet: https://stackoverflow.com/questions/7889228/how-to-prevent-reflectiontypeloadexception-when-calling-assembly-gettypes
        /// </summary>
        /// <param name="assembly">The assembly to search.</param>
        /// <returns>A list of loadable types in the given assembly.</returns>
        public static IEnumerable<Type> GetLoadableTypes(Assembly assembly)
        {
            try
            {
                return assembly.GetTypes();
            }
            catch (ReflectionTypeLoadException e)
            {
                return e.Types.Where(t => t != null);
            }
        }


        /// <summary>
        /// Fetch methods of the given type that have the given return value type (if loadable).
        /// </summary>
        /// <param name="type">The type to search the method list of.</param>
        /// <param name="returnValueType">The value type that the method must return.</param>
        /// <returns>A list of methods that have the desired return value type.</returns>
        [System.Diagnostics.CodeAnalysis.SuppressMessage("Design", "CA1031:Keine allgemeinen Ausnahmetypen abfangen", Justification = "<Ausstehend>")]
        public static IList<MethodInfo> GetLoadableReturnValueTypeMethods(Type type, Type returnValueType)
        {
            IList<MethodInfo> returnValueTypeMethods = new List<MethodInfo>();
            foreach (MethodInfo m in type.GetMethods())
            {
                try
                {
                    if (m.ReturnType == returnValueType)
                    {
                        returnValueTypeMethods.Add(m);
                    }
                }
                catch (Exception)
                {
                    // ignored
                }
            }

            return returnValueTypeMethods;
        }

        /// <summary>
        /// Fetch the type with the given class name.
        /// In case of multiple matches, null is returned.
        /// </summary>
        /// <param name="className">The name of the desired type.</param>
        /// <returns>The type with the given name.</returns>
        public static Type GetTypeByClassName(string className)
        {
            var types = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(s => GetLoadableTypes(s))
                .Where(p => string.Equals(p.Name, className, StringUtil.ComparisonIgnoreCase)).ToList();

            return types.Count == 1 ? types.First() : null;
        }

        /// <summary>
        /// Obtains the values of an enum type.
        /// </summary>
        /// <param name="enumType">The enum to read the values from.</param>
        /// <returns>A list of enum values.</returns>
        public static List<object> GetEnumValues(Type enumType)
        {
            List<object> enumValues = new();
            foreach (object val in Enum.GetValues(enumType))
            {
                enumValues.Add(val);
            }

            return enumValues;
        }

        /// <summary>
        /// Looks for methods in the currently loaded assemblies that return a value of the given type.
        /// <remarks>
        /// This is used to initialize delegate methods in configuration contexts through a JSON configuration file:
        /// There are pre-defined methods (e.g. in <see cref="riscsw.ibex.core.configurationmanager.TabuSearchConfigProvider"/>)
        /// returning callback methods that can be wrapped by the delegates in the configuration contexts.
        /// These methods can then be used to instantiate the delegates.
        /// </remarks>
        /// </summary>
        /// <param name="returnValueType">The value type that must be returned by the methods.</param>
        /// <returns>A list of methods returning the given value type.</returns>
        public static IList<MethodInfo> GetDelegateImplementations(Type returnValueType)
        {
            IEnumerable<MethodInfo> methods = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(s => GetLoadableTypes(s))
                .SelectMany(x => GetLoadableReturnValueTypeMethods(x, returnValueType));
            IEnumerable<MethodInfo> retMethods = methods.Where(m => !m.IsVirtual);
            return retMethods.ToList();
        }

        /// <summary>
        /// Returns a delegate of the given type instantiated with a pre-defined method.
        /// <remarks>
        /// This is used to initialize delegate methods in configuration contexts through a JSON configuration file:
        /// There are pre-defined methods (e.g. in <see cref="riscsw.ibex.core.configurationmanager.TabuSearchConfigProvider"/>)
        /// returning callback methods that can be wrapped by the delegates in the configuration contexts.
        /// These methods can then be used to instantiate the delegates.
        /// </remarks>
        /// </summary>
        /// <param name="returnValueType">The delegate type (which is returned by the pre-defined methods returning the callback methods).</param>
        /// <param name="methodName">The name of the method returning the callback that should be added to the delegate's invocation list.</param>
        /// <param name="args">The method parameters.</param>
        /// <returns>A delegate instantiated with the given method.</returns>
        public static Delegate GetDelegateImplementation(Type returnValueType, string methodName, object[] args)
        {
            IList<MethodInfo> delegateImplementations = GetDelegateImplementations(returnValueType);
            MethodInfo mInfo = delegateImplementations.FirstOrDefault(i => i.Name.Contains(methodName, StringUtil.ComparisonIgnoreCase));
            if (mInfo != null)
            {
                return (Delegate)mInfo.Invoke(null, args);
            }

            return null;
        }

        /// <summary>
        /// Checks if the given type is a delegate.
        /// </summary>
        /// <param name="type">The type to evaluate.</param>
        /// <returns>True if the type is a delegate.</returns>
        public static bool IsDelegate(Type type)
        {
            return typeof(Delegate).IsAssignableFrom(type.BaseType);
        }

        /// <summary>
        /// Checks if the given type is a numeric type.
        /// </summary>
        /// <param name="type">The type to evaluate.</param>
        /// <returns>True if the type is numeric.</returns>
        public static bool IsNumeric(Type type)
        {
            HashSet<Type> numericTypes = new()
            {
                typeof(decimal),
                typeof(byte),
                typeof(sbyte),
                typeof(short),
                typeof(ushort),
                typeof(int),
                typeof(uint),
                typeof(long),
                typeof(ulong),
                typeof(double),
                typeof(float)
            };
            return numericTypes.Contains(type);
        }

        /// <summary>
        /// Looks for a method with the given name in the currently loaded assemblies.
        /// </summary>
        /// <param name="methodName">The required name of the method.</param>
        /// <returns>The method with the given name (if found).</returns>
        public static MethodInfo GetMethodByName(string methodName)
        {
            IEnumerable<MethodInfo> methods = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(s => GetLoadableTypes(s))
                .SelectMany(x => x.GetMethods());
            MethodInfo retMethod = methods.FirstOrDefault(m => string.Equals(m.Name, methodName, StringUtil.ComparisonIgnoreCase) && !m.IsVirtual);
            return retMethod;
        }

        /// <summary>
        /// Returns a list of constructors of the given class.
        /// </summary>
        /// <param name="className">The name of the class.</param>
        /// <returns>A list of constructor infos.</returns>
        public static IList<ConstructorInfo> GetConstructorsByClassName(string className)
        {
            Type t = GetTypeByClassName(className);
            return t.GetConstructors().ToList();
        }

        /// <summary>
        /// Case-insensitive dictionary lookup.
        /// </summary>
        /// <param name="dict">The dictionary to find the key in.</param>
        /// <param name="key">The key to look for in a case-insensitive manner.</param>
        /// <returns>The value, if key is found in dictionary. Otherwise null.</returns>
        public static string GetDictionaryValueCaseInsensitive(IDictionary<string, string> dict, string key)
        {
            if (dict.Any(x => string.Equals(x.Key, key, StringUtil.ComparisonIgnoreCase)))
            {
                return dict.First(x => string.Equals(x.Key, key, StringUtil.ComparisonIgnoreCase)).Value;
            }

            return null;
        }
    }
}
