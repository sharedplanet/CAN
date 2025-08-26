#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 22:35:25 2025

@author: manickamvalliappan
"""

var table = ee.FeatureCollection("projects/friendly-aura-407316/assets/Egypt_Kenya_Namibia");

var selectedCountries = ['Egypt', 'Kenya', 'Namibia'];

var cleanTable = table.filter(ee.Filter.and(
  ee.Filter.neq('Latitude', null),
  ee.Filter.neq('Longitude', null),
  ee.Filter.inList('Country/area', selectedCountries)
));

var withGeometry = cleanTable.map(function(f) {
  var lon = ee.Number.parse(f.get('Longitude'));
  var lat = ee.Number.parse(f.get('Latitude'));
  var point = ee.Geometry.Point([lon, lat]);
  return ee.Feature(point).copyProperties(f);
});

var waterRisk = ee.FeatureCollection('WRI/Aqueduct_Water_Risk/V4/baseline_annual');
var validRisk = waterRisk.filter(ee.Filter.gt('bws_cat', -1));

var spatialJoin = ee.Join.saveBest({
  matchKey: 'matched',
  measureKey: 'distance'
});

var joined = spatialJoin.apply(withGeometry, validRisk, ee.Filter.intersects({
  leftField: '.geo',
  rightField: '.geo',
  maxError: 10
}));

var final = joined.map(function(f) {
  var match = ee.Feature(f.get('matched'));
  var riskCat = ee.Algorithms.If(match, match.get('bws_cat'), -1);
  return f.set('bws_cat', riskCat);
});

var categoryCounts = ee.List.sequence(-1, 4).map(function(cat) {
  cat = ee.Number(cat);
  var count = final.filter(ee.Filter.eq('bws_cat', cat)).size();
  return ee.Dictionary({
    category: cat,
    count: count
  });
});

print('Number of renewable plants per baseline water stress category (Egypt, Kenya, Namibia):', categoryCounts);

var outputTable = final.map(function(f) {
  return ee.Feature(null, {
    name: f.get('Plant / Project name'),
    country: f.get('Country/area'),
    bws_cat: f.get('bws_cat')
  });
});
print('Sample plant names with stress categories:', outputTable.limit(50));

Export.table.toDrive({
  collection: final.limit(500).map(function(f) {
    return ee.Feature(null, {
      'Plant_Name': f.get('Plant / Project name'),
      'Latitude': f.geometry().coordinates().get(1),
      'Longitude': f.geometry().coordinates().get(0),
      'Capacity_MW': f.get('Capacity (MW)'),
      'Water_Stress_Category': f.get('bws_cat'),
      'Country': f.get('Country/area')
    });
  }),
  description: 'Renewable_Plants_Water_Stress_Sample_500',
  fileFormat: 'CSV'
});