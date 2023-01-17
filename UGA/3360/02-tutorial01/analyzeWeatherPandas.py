import pandas as pd

data = pd.read_csv('weather.csv')
print( " 1: ----- " )
print (data)
print( " 2: ----- " )
print( data.columns )
print( " 3: ----- " )
print( data.date )
print( " 4: ----- " )
print( data.tmin )
print( " 5: ----- " )
print( data.tmax )

print( " 6: ----- " )
print(type(data))
#exit(0)
# print( data[5][0] )   ## doesn't work
# print( data[[0,1]])    ## doesn't work

# select the 3rd, 4th, and 5th rows of the DataFrame .iloc selects integeger value index value.

# below indexing [] includes a list of rows. so another [], making double brackets
print( f"3rd, 4th, & 5th rows: data.iloc[[2, 3, 4]]  : { data.iloc[[2, 3, 4]]}" )

# below indexing []  includes a slice
print( f"3rd, 4th, & 5th rows: data.iloc[2:5] :  { data.iloc[2:5]}" )

print( " 7: ----- " )
print( data[:5] )


print( " 8: ----- " )
print( data.loc[2:3])

print( " 9: ----- " )
print( data.loc[0])

## continue practicing --
## https://pandas.pydata.org/docs/user_guide/indexing.html
print( " 10: ----- " )

print( data.loc[ data['tmin'] > 70, ['tmin','tmax']])
#print( data.loc[:100,data.loc['temperaturemin'] >70 ])
exit(0)
##print( data.loc['temperaturemin'] )

print( " 11: ---- min --- " )
print(data[['temperaturemin']])

print( " 12: ----- max -- " )
print(data[u'temperaturemax'])

print( " 13: ----- max -- " )
print(data['temperaturemax'])


print( " 12: ----- " )

## exit(1)
print(data[['tmin', 'tmax']])

print( " 13 Mean is: ----- " )
## ADD from slides ...


# write DATA
# index - removes the index numbers (0, 1, 2, ... )
data.to_csv("O8-write_data.csv", index=False )



